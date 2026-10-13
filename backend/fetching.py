"""Downloading web pages safely.

1. The URL must be public: http(s) only, and the host must not resolve to a private,
   loopback or link-local address (otherwise anyone could make our server read
   `http://localhost:...` or the cloud metadata endpoint — an SSRF attack).
   Every redirect hop is checked again.
2. A plain HTTPS request (fast, free, keeps the raw HTML with its structured price data).
   If the site refuses it, we ask once more as an openly named crawler: many shops
   (e.g. Shopify stores behind Cloudflare) turn away a browser-like request that doesn't
   come from a real browser, but welcome a bot that says what it is.
3. If the site still refuses us (403/429/bot page), Tavily Extract fetches it from its
   servers. We don't try to disguise ourselves or bypass bot protection.
"""

import asyncio
import ipaddress
import logging
import re
import socket
from contextlib import AsyncExitStack
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
CRAWLER_HEADERS = HEADERS | {
    "User-Agent": (
        "Mozilla/5.0 (compatible; RivalscopeBot/0.2; "
        "+https://github.com/trigonosaurus-rgb/e-commerce-ai-monitoring)"
    )
}
_BLOCK_MARKERS = re.compile(
    r"captcha|access denied|are you a robot|verify you are human|just a moment|cf-chl|"
    r"enable javascript and cookies",
    re.IGNORECASE,
)
# Shops with several "markets" (built into Shopify) show visitors from abroad another
# price: without local VAT or converted to another currency. This cookie asks for the
# price local customers see. Other sites simply ignore it.
COUNTRY_CODES = {
    "united states": "US",
    "united kingdom": "GB",
    "canada": "CA",
    "australia": "AU",
    "ireland": "IE",
    "germany": "DE",
    "austria": "AT",
    "switzerland": "CH",
    "france": "FR",
    "belgium": "BE",
    "netherlands": "NL",
    "luxembourg": "LU",
    "spain": "ES",
    "portugal": "PT",
    "italy": "IT",
    "poland": "PL",
    "czech republic": "CZ",
    "sweden": "SE",
    "denmark": "DK",
    "norway": "NO",
    "finland": "FI",
}
GENERIC_CCTLDS = {"io", "co", "ai", "me", "tv", "cc", "fm", "ly", "gg", "to", "sh", "ws", "eu"}
MAX_REDIRECTS = 5
# clearly a file, not a product page: no point trying another route
FILE_TYPES = (
    "application/pdf",
    "image/",
    "video/",
    "audio/",
    "application/zip",
    "application/octet-stream",
)


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


def market_country_code(url: str, market: str | None = None) -> str | None:
    """ISO code of the shop's home market: from the product's market, else the domain."""
    if market and (code := COUNTRY_CODES.get(market.strip().lower())):
        return code
    tld = (urlsplit(url).hostname or "").rsplit(".", 1)[-1]
    if len(tld) != 2 or tld in GENERIC_CCTLDS:
        return None
    return "GB" if tld == "uk" else tld.upper()


def foreign_domain(domain: str, market: str | None) -> str | None:
    """The country a domain clearly belongs to, if it is not the market's: by its country
    TLD (shop.be for the Dutch market) or a country subdomain (us.brand.com for the UK)."""
    home = COUNTRY_CODES.get((market or "").strip().lower())
    if not home:
        return None
    labels = domain.lower().split(".")
    codes = {market_country_code("https://" + domain)}
    if len(labels) > 2 and len(labels[0]) == 2:
        codes.add("GB" if labels[0] == "uk" else labels[0].upper())
    known = set(COUNTRY_CODES.values())
    return next((c for c in codes if c in known and c != home), None)


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


async def _fetch_direct(
    url: str, client: httpx.AsyncClient, headers: dict[str, str]
) -> tuple[int, Page]:
    settings = get_settings()
    current = url
    for _ in range(MAX_REDIRECTS + 1):
        await ensure_public_url(current)
        async with client.stream("GET", current, headers=headers) as response:
            if response.is_redirect:
                location = response.headers.get("location")
                if not location:
                    raise FetchError("The site sent a broken redirect.")
                current = urljoin(current, location)
                continue
            kind = response.headers.get("content-type", "").lower().split(";")[0].strip()
            if kind.startswith(FILE_TYPES):
                raise PermanentFetchError(f"The link is not a web page ({kind}).")
            if kind and "html" not in kind:
                # e.g. text/plain "Access denied" from bot protection: worth another route
                raise FetchError(f"the site answered with {kind} instead of a page")
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


async def _try_direct(url: str, client: httpx.AsyncClient, headers: dict) -> Page | str:
    """The page, or the reason the site refused it (dead links and unsafe URLs raise)."""
    try:
        status, page = await _fetch_direct(url, client, headers)
    except UnsafeURLError, PermanentFetchError:
        raise
    except FetchError as exc:
        return str(exc)
    except httpx.TimeoutException:
        return "the site did not respond in time"
    except httpx.HTTPError as exc:
        return f"connection error ({type(exc).__name__})"
    if status in (404, 410):
        raise PermanentFetchError(
            f"Page not found (HTTP {status}) — the product may have been removed."
        )
    if status == 200 and not _looks_blocked(status, page.text):
        if urlsplit(url).path.strip("/") and not urlsplit(page.url).path.strip("/"):
            # shops often send links of deleted products to the home page, whose
            # "featured product" data would otherwise be read as this product
            raise PermanentFetchError(
                "The link now opens the shop's home page — the product may have been removed."
            )
        return page
    return f"HTTP {status}" if status != 200 else "the site showed a bot-check page"


async def fetch_page(
    url: str, *, client: httpx.AsyncClient | None = None, market: str | None = None
) -> Page:
    """Returns the page or raises FetchError with a user-readable reason.
    `market` (e.g. "united kingdom") asks multi-country shops for their local price."""
    settings = get_settings()
    await ensure_public_url(url)
    country = market_country_code(url, market)
    cookie = {"Cookie": f"localization={country}"} if country else {}
    async with AsyncExitStack() as stack:
        if client is None:
            client = await stack.enter_async_context(
                httpx.AsyncClient(timeout=settings.fetch_timeout_seconds, follow_redirects=False)
            )
        result = await _try_direct(url, client, HEADERS | cookie)
        if isinstance(result, str) and not result.startswith(("the site did not", "connection")):
            log.info("%s refused a browser-like request (%s), asking as a crawler", url, result)
            second = await _try_direct(url, client, CRAWLER_HEADERS | cookie)
            if isinstance(second, Page):
                return second
        if isinstance(result, Page):
            return result
    reason = result
    if settings.search_configured:
        log.info("Direct fetch of %s failed (%s), trying Tavily Extract", url, reason)
        if page := await fetch_via_tavily(url):
            return page
        reason += "; the backup reader (Tavily) was blocked too"
    raise FetchError(f"Couldn't load the page: {reason}.")


async def fetch_via_tavily(url: str) -> Page | None:
    """Tavily renders the page on its side — also used when a page loaded fine but
    showed its price only after running JavaScript."""
    try:
        text = await search.extract_page(url)
    except Exception as exc:  # a fallback must never hide the original problem
        log.warning("Tavily Extract failed for %s: %s", url, exc)
        return None
    return Page(url=url, text=text, html=None, via="tavily") if text else None
