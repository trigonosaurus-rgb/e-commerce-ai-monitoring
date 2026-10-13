"""Email via plain SMTP (works with Resend, Mailgun, Gmail app passwords, any provider)."""

import asyncio
import logging
import smtplib
import ssl
from email.message import EmailMessage
from email.utils import make_msgid, parseaddr

from backend.config import get_settings

log = logging.getLogger(__name__)


class EmailError(RuntimeError):
    pass


def _send_sync(to: str, subject: str, text: str, html: str) -> str:
    """Returns the server's answer to the message, which carries the provider's message id:
    the trail to follow in its dashboard when a mail was accepted but never arrived."""
    settings = get_settings()
    if not settings.email_configured:
        raise EmailError("SMTP is not configured.")
    sender = parseaddr(settings.smtp_from)[1]
    message = EmailMessage()
    message["From"] = settings.smtp_from
    message["To"] = to
    message["Subject"] = subject
    message["Message-ID"] = make_msgid(domain=sender.rpartition("@")[2] or None)
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
        # the low-level steps instead of send_message(), to keep the server's replies
        for code, reply in (smtp.mail(sender), smtp.rcpt(to)):
            if code not in (250, 251):
                raise EmailError(f"The mail server refused it: {code} {reply.decode()}")
        code, reply = smtp.data(message.as_bytes())
        if code != 250:
            raise EmailError(f"The mail server refused it: {code} {reply.decode()}")
        return reply.decode(errors="replace")


async def send_email(to: str, subject: str, text: str, html: str) -> None:
    try:
        reply = await asyncio.to_thread(_send_sync, to, subject, text, html)
    except (OSError, smtplib.SMTPException) as exc:
        raise EmailError(f"Email to {to} failed: {exc}") from exc
    log.info("Email “%s” to %s accepted by %s: %s", subject, to, get_settings().smtp_host, reply)
