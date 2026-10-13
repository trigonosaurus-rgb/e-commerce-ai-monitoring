"""Telegram bot: sending alerts and linking a user's chat.

Linking works without a public webhook URL: the UI gives the user a deep link
`t.me/<bot>?start=<one-time token>`, the user presses Start, and the long-polling loop
below receives `/start <token>` and stores that chat id for the user.
"""

import asyncio
import logging

import httpx
from sqlmodel import select

from backend.config import get_settings
from backend.database import session_scope
from backend.models import User

log = logging.getLogger(__name__)


class TelegramError(RuntimeError):
    pass


async def call(method: str, params: dict, *, http_timeout: float = 15) -> dict | list:
    token = get_settings().telegram_bot_token
    if token is None:
        raise TelegramError("TELEGRAM_BOT_TOKEN is not set.")
    url = f"https://api.telegram.org/bot{token.get_secret_value()}/{method}"
    async with httpx.AsyncClient(timeout=http_timeout) as client:
        response = await client.post(url, json=params)
    payload = response.json()
    if not payload.get("ok"):
        raise TelegramError(payload.get("description") or f"HTTP {response.status_code}")
    return payload["result"]


async def send_message(chat_id: str, html_text: str) -> None:
    await call(
        "sendMessage",
        {
            "chat_id": chat_id,
            "text": html_text,
            "parse_mode": "HTML",
            "link_preview_options": {"is_disabled": True},
        },
    )


def bot_username() -> str | None:
    """TELEGRAM_BOT_USERNAME if set, otherwise the name Telegram reported for the token."""
    return get_settings().telegram_bot_username or poller.username


class TelegramPoller:
    def __init__(self) -> None:
        self.status = "stopped"
        self.last_error: str | None = None
        self.username: str | None = None  # learned from getMe, so it needn't be configured

    async def run_forever(self) -> None:
        offset: int | None = None
        while True:
            try:
                if self.username is None:
                    self.username = (await call("getMe", {}))["username"]
                updates = await self._get_updates(offset)
                self.status, self.last_error = "running", None
                for update in updates:
                    offset = update["update_id"] + 1
                    message = update.get("message") or {}
                    if message.get("text"):
                        await self._handle(str(message["chat"]["id"]), message["text"].strip())
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # network hiccups must not kill the loop
                self.status, self.last_error = "error", str(exc)
                log.warning("Telegram polling failed: %s", exc)
                await asyncio.sleep(15)

    async def _get_updates(self, offset: int | None) -> list:
        # long polling: Telegram holds the request up to 30 s until a message arrives
        params = {"timeout": 30, "allowed_updates": ["message"]}
        if offset is not None:
            params["offset"] = offset
        return await call("getUpdates", params, http_timeout=45)

    async def _handle(self, chat_id: str, text: str) -> None:
        app = get_settings().app_name
        if text.startswith("/start"):
            token = text.removeprefix("/start").strip()
            with session_scope() as session:
                user = None
                if token:
                    user = session.exec(
                        select(User).where(User.telegram_link_token == token)
                    ).first()
                if user is None:
                    reply = (
                        f"Hi! To get {app} alerts here, open Settings → Notifications "
                        "and press “Connect Telegram”."
                    )
                else:
                    user.telegram_chat_id = chat_id
                    user.telegram_link_token = None
                    user.notify_telegram = True
                    session.commit()
                    reply = f"✅ Connected. {app} price alerts for {user.email} will arrive here."
            await send_message(chat_id, reply)
        elif text.startswith("/stop"):
            with session_scope() as session:
                for user in session.exec(select(User).where(User.telegram_chat_id == chat_id)):
                    user.telegram_chat_id = None
                    user.notify_telegram = False
                session.commit()
            await send_message(chat_id, "Alerts are turned off for this chat.")


poller = TelegramPoller()
