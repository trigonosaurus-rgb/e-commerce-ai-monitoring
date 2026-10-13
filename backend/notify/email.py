"""Email via plain SMTP (works with Gmail app passwords, Resend, Mailgun, any provider)."""

import asyncio
import smtplib
import ssl
from email.message import EmailMessage

from backend.config import get_settings


class EmailError(RuntimeError):
    pass


def _send_sync(to: str, subject: str, text: str, html: str) -> None:
    settings = get_settings()
    if not settings.email_configured:
        raise EmailError("SMTP is not configured.")
    message = EmailMessage()
    message["From"] = settings.smtp_from
    message["To"] = to
    message["Subject"] = subject
    message.set_content(text)
    message.add_alternative(html, subtype="html")

    context = ssl.create_default_context()
    smtp_cls = smtplib.SMTP_SSL if settings.smtp_ssl else smtplib.SMTP
    kwargs = {"context": context} if settings.smtp_ssl else {}
    with smtp_cls(settings.smtp_host, settings.smtp_port, timeout=20, **kwargs) as smtp:
        if not settings.smtp_ssl:
            smtp.starttls(context=context)
        if settings.smtp_user and settings.smtp_password:
            smtp.login(settings.smtp_user, settings.smtp_password.get_secret_value())
        smtp.send_message(message)


async def send_email(to: str, subject: str, text: str, html: str) -> None:
    try:
        await asyncio.to_thread(_send_sync, to, subject, text, html)
    except (OSError, smtplib.SMTPException) as exc:
        raise EmailError(f"Email to {to} failed: {exc}") from exc
