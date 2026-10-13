"""Delivering alerts to the channels each user picked in Settings.

In-app alerts always exist (they are rows in the Alert table). Telegram and email are
optional extras; a failing channel is recorded on the alert and never breaks a check.
"""

import html
import logging

from backend.config import get_settings
from backend.database import session_scope
from backend.models import Alert, User
from backend.notify import email, telegram

log = logging.getLogger(__name__)


def app_link(path: str) -> str:
    return get_settings().public_url.rstrip("/") + path


def _telegram_text(title: str, message: str, links: list[dict[str, str]]) -> str:
    parts = [f"<b>{html.escape(title)}</b>", html.escape(message)]
    if links:
        parts.append(
            " · ".join(
                f'<a href="{html.escape(link["url"])}">{html.escape(link["label"])}</a>'
                for link in links
            )
        )
    return "\n\n".join(parts)


def _email_bodies(title: str, message: str, links: list[dict[str, str]]) -> tuple[str, str]:
    text = "\n\n".join([title, message, *(f"{link['label']}: {link['url']}" for link in links)])
    items = "".join(
        f'<li><a href="{html.escape(link["url"])}">{html.escape(link["label"])}</a></li>'
        for link in links
    )
    body = (
        f"<h2 style='font-family:sans-serif'>{html.escape(title)}</h2>"
        f"<p style='font-family:sans-serif;line-height:1.5'>{html.escape(message)}</p>"
        f"<ul style='font-family:sans-serif'>{items}</ul>"
    )
    return text, body


async def send_to_user(
    user: User, title: str, message: str, links: list[dict[str, str]]
) -> dict[str, str]:
    """Returns {channel: "sent" | error message} for every channel the user enabled."""
    settings = get_settings()
    results: dict[str, str] = {}
    if user.notify_telegram:
        if not settings.telegram_configured:
            results["telegram"] = "Telegram bot is not configured on the server."
        elif not user.telegram_chat_id:
            results["telegram"] = "Telegram is not connected yet."
        else:
            try:
                await telegram.send_message(
                    user.telegram_chat_id, _telegram_text(title, message, links)
                )
                results["telegram"] = "sent"
            except Exception as exc:
                results["telegram"] = str(exc)
    if user.notify_email:
        if not settings.email_configured:
            results["email"] = "Email (SMTP) is not configured on the server."
        else:
            text, body = _email_bodies(title, message, links)
            try:
                await email.send_email(
                    user.alert_email or user.email, f"[{settings.app_name}] {title}", text, body
                )
                results["email"] = "sent"
            except Exception as exc:
                results["email"] = str(exc)
    for channel, result in results.items():
        if result != "sent":
            log.warning("Notification via %s failed for user %s: %s", channel, user.id, result)
    return results


async def dispatch(alert_id: int) -> None:
    with session_scope() as session:
        alert = session.get(Alert, alert_id)
        user = session.get(User, alert.user_id)
    if user.is_demo:
        return
    links = list(alert.links)
    if alert.product_id:
        links.append(
            {
                "label": "Open in " + get_settings().app_name,
                "url": app_link(f"/product/?id={alert.product_id}"),
            }
        )
    results = await send_to_user(user, alert.title, alert.message, links)
    with session_scope() as session:
        alert = session.get(Alert, alert_id)
        alert.delivered = [
            channel if result == "sent" else f"{channel}_failed"
            for channel, result in results.items()
        ]
        session.commit()


async def notify_owner(text: str) -> None:
    """Sends a plain message to the app owner (used for access requests)."""
    settings = get_settings()
    if settings.telegram_configured and settings.owner_telegram_chat_id:
        try:
            await telegram.send_message(settings.owner_telegram_chat_id, html.escape(text))
        except Exception as exc:
            log.warning("Could not notify the owner via Telegram: %s", exc)
