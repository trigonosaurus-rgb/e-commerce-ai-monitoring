"""Thin wrapper around Tavily (web search + page extraction).

Kept in one place so tests can replace `search_web` / `extract_page` with fakes and so a
different provider can be swapped in without touching the agent.
"""

import logging
from dataclasses import dataclass
from urllib.parse import urlsplit

from tavily import AsyncTavilyClient, BadRequestError

from backend.config import get_settings

log = logging.getLogger(__name__)


class SearchNotConfigured(RuntimeError):
    pass


@dataclass
class SearchResult:
    url: str
    title: str
    snippet: str
    domain: str
    favicon: str | None = None


def domain_of(url: str) -> str:
    host = (urlsplit(url).hostname or "").lower()
    return host.removeprefix("www.")


def _client() -> AsyncTavilyClient:
    settings = get_settings()
    if not settings.search_configured:
        raise SearchNotConfigured("TAVILY_API_KEY is not set — web search is unavailable.")
    return AsyncTavilyClient(api_key=settings.tavily_api_key.get_secret_value())


async def search_web(
    query: str,
    *,
    country: str | None = None,
    exclude_domains: list[str] | None = None,
    include_domains: list[str] | None = None,
    max_results: int = 8,
) -> list[SearchResult]:
    client = _client()
    params = {
        "search_depth": "basic",
        "topic": "general",
        "max_results": max_results,
        "exclude_domains": exclude_domains or None,
        "include_domains": include_domains or None,
        "include_favicon": True,
    }
    try:
        response = await client.search(query, country=country, **params)
    except BadRequestError as exc:
        if not country or "country" not in str(exc).lower():
            raise
        # Tavily only accepts its own list of country names; search globally instead.
        log.warning("Tavily rejected country=%r, retrying without it", country)
        response = await client.search(query, **params)
    return [
        SearchResult(
            url=item["url"],
            title=item.get("title") or "",
            snippet=(item.get("content") or "")[:400],
            domain=domain_of(item["url"]),
            favicon=item.get("favicon"),
        )
        for item in response.get("results", [])
        if item.get("url")
    ]


async def extract_page(url: str) -> str | None:
    """Fetches a page through Tavily's servers. Used when a site refuses our direct request."""
    response = await _client().extract(urls=[url], extract_depth="advanced", format="markdown")
    for item in response.get("results", []):
        content = item.get("raw_content")
        if content:
            return content
    for item in response.get("failed_results", []):
        log.info("Tavily could not extract %s: %s", url, item.get("error"))
    return None
