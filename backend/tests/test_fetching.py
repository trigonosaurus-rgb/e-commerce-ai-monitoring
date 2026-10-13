import httpx
import pytest

from backend import fetching
from backend.fetching import (
    FetchError,
    PermanentFetchError,
    UnsafeURLError,
    ensure_public_url,
    fetch_page,
    foreign_domain,
    market_country_code,
    normalize_url,
)

pytestmark = pytest.mark.anyio
PUBLIC = "http://93.184.215.14"  # an IP literal: no DNS lookup needed in tests


def test_normalize_url_adds_scheme():
    assert normalize_url("  shop.example.com/p/1 ") == "https://shop.example.com/p/1"
    assert normalize_url("http://shop.example.com") == "http://shop.example.com"


@pytest.mark.parametrize(
    "url",
    [
        "file:///C:/Windows/win.ini",
        "ftp://example.com/file",
        "http://localhost:8000/api",
        "http://127.0.0.1/admin",
        "http://10.0.0.5/",
        "http://192.168.1.1/",
        "http://169.254.169.254/latest/meta-data/",  # cloud metadata endpoint
        "http://[::1]/",
        "http://user:pass@example.com/",
        "http://printer.local/",
    ],
)
async def test_private_and_odd_urls_are_rejected(url):
    with pytest.raises(UnsafeURLError):
        await ensure_public_url(url)


async def test_domain_resolving_to_private_ip_is_rejected(monkeypatch):
    async def fake_resolve(host):
        return ["10.1.2.3"]

    monkeypatch.setattr(fetching, "resolve_host", fake_resolve)
    with pytest.raises(UnsafeURLError):
        await ensure_public_url("https://innocent-looking.example.com/")


def _client(handler) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.MockTransport(handler), follow_redirects=False)


async def test_redirect_to_private_network_is_blocked():
    def handler(request):
        return httpx.Response(302, headers={"location": "http://127.0.0.1/admin"})

    async with _client(handler) as client:
        with pytest.raises(UnsafeURLError):
            await fetch_page(f"{PUBLIC}/product", client=client)


async def test_successful_fetch_follows_redirect_and_returns_text():
    def handler(request):
        if request.url.path == "/old":
            return httpx.Response(301, headers={"location": "/new"})
        html = "<html><head><title>Lamp</title></head><body><main>" + "Oak lamp. " * 50
        return httpx.Response(200, html=html + "</main></body></html>")

    async with _client(handler) as client:
        page = await fetch_page(f"{PUBLIC}/old", client=client)
    assert page.url.endswith("/new")
    assert page.via == "direct"
    assert page.text.startswith("Lamp")


async def test_blocked_page_without_fallback_explains_why():
    def handler(request):
        return httpx.Response(403, html="<html><body>Access denied</body></html>")

    async with _client(handler) as client:
        with pytest.raises(FetchError, match="HTTP 403"):
            await fetch_page(f"{PUBLIC}/product", client=client)


async def test_missing_page_is_a_permanent_error():
    async with _client(lambda request: httpx.Response(404, html="gone")) as client:
        with pytest.raises(PermanentFetchError, match="not found"):
            await fetch_page(f"{PUBLIC}/product", client=client)


async def test_non_html_is_rejected():
    def handler(request):
        return httpx.Response(200, content=b"%PDF", headers={"content-type": "application/pdf"})

    async with _client(handler) as client:
        with pytest.raises(PermanentFetchError, match="not a web page"):
            await fetch_page(f"{PUBLIC}/manual.pdf", client=client)


async def test_plain_text_answer_is_treated_as_a_block_not_a_dead_link():
    def handler(request):
        return httpx.Response(200, text="Access Denied", headers={"content-type": "text/plain"})

    async with _client(handler) as client:
        with pytest.raises(FetchError, match="text/plain instead of a page") as info:
            await fetch_page(f"{PUBLIC}/product", client=client)
    assert not isinstance(info.value, PermanentFetchError)


async def test_refused_browser_request_is_retried_as_named_crawler():
    agents = []

    def handler(request):
        agents.append(request.headers["user-agent"])
        if "RivalscopeBot" not in request.headers["user-agent"]:
            return httpx.Response(429, html="<html><body>Too many requests</body></html>")
        return httpx.Response(200, html="<html><body><main>" + "Linen towel. " * 40 + "</main>")

    async with _client(handler) as client:
        page = await fetch_page(f"{PUBLIC}/products/towel", client=client)
    assert page.via == "direct" and "Linen towel" in page.text
    assert len(agents) == 2 and "RivalscopeBot" in agents[1]


async def test_product_link_landing_on_home_page_counts_as_removed():
    def handler(request):
        if request.url.path == "/products/kettle":
            return httpx.Response(301, headers={"location": "/"})
        return httpx.Response(200, html="<html><body><main>" + "Featured grinder " * 40)

    async with _client(handler) as client:
        with pytest.raises(PermanentFetchError, match="home page"):
            await fetch_page(f"{PUBLIC}/products/kettle", client=client)


def test_market_country_comes_from_market_or_domain():
    assert market_country_code("https://shop.example.com/p", "United Kingdom") == "GB"
    assert market_country_code("https://www.lakeland.co.uk/products/tin") == "GB"
    assert market_country_code("https://mediamarkt.pl/p") == "PL"
    assert market_country_code("https://brand.io/p") is None  # .io is not a country shop
    assert market_country_code("https://us.lacabra.com/p") is None


def test_foreign_domains_are_recognised():
    assert foreign_domain("coolblue.be", "netherlands") == "BE"
    assert foreign_domain("us.home-appliances.philips", "united kingdom") == "US"
    assert foreign_domain("fr.fnac.ch", "france") == "CH"
    assert foreign_domain("johnlewis.com", "united kingdom") is None
    assert foreign_domain("argos.co.uk", "united kingdom") is None
    assert foreign_domain("shop.example.de", None) is None


async def test_shop_is_asked_for_its_local_price():
    cookies = []

    def handler(request):
        cookies.append(request.headers.get("cookie"))
        return httpx.Response(200, html="<html><body><main>" + "Brownie tin. " * 40)

    async with _client(handler) as client:
        await fetch_page(f"{PUBLIC}/products/tin", client=client, market="united kingdom")
    assert cookies == ["localization=GB"]
