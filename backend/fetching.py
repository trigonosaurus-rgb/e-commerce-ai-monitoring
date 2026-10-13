"""Downloading web pages safely.

1. The URL must be public: http(s) only, and the host must not resolve to a private,
   loopback or link-local address (otherwise anyone could make our server read
   `http://localhost:...` or the cloud metadata endpoint — an SSRF attack).
   Every redirect hop is checked again.
2. A plain HTTPS request (fast, free, keeps the raw HTML with its structured price data).
3. If the site refuses us (403/429/bot page), Tavily Extract fetches it from its servers.
   We don't try to disguise ourselves or bypass bot protection.
"""

import asyncio
import ipaddress
import logging
import re
import socket
from dataclasses import dataclass
from urllib.parse import urljoin, urlsplit

import httpx
from bs4 import BeautifulSoup, UnicodeDammit

from backend import search
from backend.config import get_settings

log = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,de;q=0.8",
}
_BLOCK_MARKERS = re.compile(
    r"captcha|access denied|are you a robot|verify you are human|just a moment|cf-chl|"
    r"enable javascript and cookies",
    re.IGNORECASE,
)
MAX_REDIRECTS = 5


class FetchError(Exception):
    """The message is written for end users and shown in the UI as is."""


class UnsafeURLError(FetchError):
    pass


class PermanentFetchError(FetchError):
    """Retrying through another route won't help (404, not an HTML page)."""


@dataclass
class Page:
    url: str  # final URL after redirects
    text: str  # readable text for the LLM and for evidence checks
    html: str | None  # None when the page came through Tavily (text only)
    via: str  # direct | tavily


def normalize_url(raw: str) -> str:
    url = raw.strip()
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url):
        url = "https://" + url
    return url


async def resolve_host(host: str) -> list[str]:
    infos = await asyncio.get_running_loop().getaddrinfo(host, None, type=socket.SOCK_STREAM)
    return [info[4][0] for info in infos]


async def ensure_public_url(url: str) -> None:
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https"):
        raise UnsafeURLError("Only http:// and https:// links are supported.")
    host = parts.hostname
    if not host:
        raise UnsafeURLError("The link has no host name.")
    if parts.username or parts.password:
        raise UnsafeURLError("Links with embedded credentials are not allowed.")
    try:
        addresses = [str(ipaddress.ip_address(host))]
    except ValueError:
        if host == "localhost" or host.endswith((".localhost", ".local", ".internal")):
            raise UnsafeURLError("Links to local network hosts are not allowed.") from None
        try:
            addresses = await resolve_host(host)
        except socket.gaierror, UnicodeError:
            raise FetchError(f"The domain {host} does not exist or can't be resolved.") from None
    for address in addresses:
        ip = ipaddress.ip_address(address.split("%")[0])
        if not ip.is_global or ip.is_multicast:
            raise UnsafeURLError("Links to private or local network addresses are not allowed.")


def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg", "iframe", "template"]):
        tag.decompose()
    main = soup.find("main") or soup.find(attrs={"role": "main"})
    root = main if main and len(main.get_text(strip=True)) > 300 else soup
    lines = [line.strip() for line in root.get_text("\n").splitlines()]
    text = "\n".join(line for line in lines if line)
    title = soup.title.get_text(strip=True) if soup.title else ""
    return f"{title}\n{text}" if title and not text.startswith(title) else text


def _looks_blocked(status: int, text: str) -> bool:
    if status in (401, 403, 429, 503):
        return True
    return len(text) < 1500 and bool(_BLOCK_MARKERS.search(text))


async def _fetch_direct(url: str, client: httpx.AsyncClient) -> tuple[int, Page]:
    settings = get_settings()
    current = url
    for _ in range(MAX_REDIRECTS + 1):
        await ensure_public_url(current)
        async with client.stream("GET", current, headers=HEADERS) as response:
            if response.is_redirect:
                location = response.headers.get("location")
                if not location:
                    raise FetchError("The site sent a broken redirect.")
                current = urljoin(current, location)
                continue
            content_type = response.headers.get("content-type", "").lower()
            if content_type and "html" not in content_type:
                kind = content_type.split(";")[0]
                raise PermanentFetchError(f"The link is not a web page ({kind}).")
            body = bytearray()
            async for chunk in response.aiter_bytes():
                body += chunk
                if len(body) >= settings.fetch_max_bytes:
                    break
            known = [response.charset_encoding] if response.charset_encoding else []
            html = UnicodeDammit(bytes(body), known).unicode_markup or ""
            page = Page(url=str(response.url), text=html_to_text(html), html=html, via="direct")
            return response.status_code, page
    raise FetchError("The site redirects too many times.")


async def fetch_page(url: str, *, client: httpx.AsyncClient | None = None) -> Page:
    """Returns the page or raises FetchError with a user-readable reason."""
    settings = get_settings()
    await ensure_public_url(url)
    reason = "unknown error"
    try:
        if client is None:
            async with httpx.AsyncClient(
                timeout=settings.fetch_timeout_seconds, follow_redirects=False
            ) as own_client:
                status, page = await _fetch_direct(url, own_client)
        else:
            status, page = await _fetch_direct(url, client)
        if status in (404, 410):
            raise PermanentFetchError(
                f"Page not found (HTTP {status}) — the product may have been removed."
            )
        if status == 200 and not _looks_blocked(status, page.text):
            return page
        reason = f"HTTP {status}" if status != 200 else "the site showed a bot-check page"
    except UnsafeURLError, PermanentFetchError:
        raise
    except FetchError as exc:
        reason = str(exc)
    except httpx.TimeoutException:
        reason = "the site did not respond in time"
    except httpx.HTTPError as exc:
        reason = f"connection error ({type(exc).__name__})"

    if settings.search_configured:
        log.info("Direct fetch of %s failed (%s), trying Tavily Extract", url, reason)
        try:
            text = await search.extract_page(url)
        except Exception as exc:  # the fallback must never hide the original reason
            log.warning("Tavily Extract failed for %s: %s", url, exc)
            text = None
        if text:
            return Page(url=url, text=text, html=None, via="tavily")
    raise FetchError(f"Couldn't load the page: {reason}.")
