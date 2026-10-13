"""Reading product data (name, identifiers, price) from a page.

Order of trust:
1. schema.org JSON-LD — what Shopify, WooCommerce, Shopware, Magento etc. publish for
   Google Shopping. Exact, machine-readable, no AI involved.
2. schema.org microdata and `product:price` meta tags — same idea, older formats.
3. LLM fallback — only if the page has no structured data. The model must quote the
   page text it read the price from, and we check that the quote really is on the page.
"""

import json
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any
from urllib.parse import urlsplit

from bs4 import BeautifulSoup

from backend import llm
from backend.config import get_settings
from backend.fetching import Page

PRODUCT_TYPES = {"product", "productgroup", "productmodel", "individualproduct"}
IN_STOCK = {"instock", "limitedavailability", "onlineonly", "instoreonly"}
OUT_OF_STOCK = {"outofstock", "soldout", "discontinued"}


@dataclass
class ProductData:
    name: str | None = None
    brand: str | None = None
    mpn: str | None = None
    gtin: str | None = None
    image: str | None = None
    price: float | None = None
    currency: str | None = None
    in_stock: bool | None = None
    method: str | None = None  # jsonld | microdata | meta | llm
    evidence: str = ""
    note: str | None = None  # why the price is missing, if it is

    @property
    def has_price(self) -> bool:
        return self.price is not None and self.price > 0 and bool(self.currency)

    def identity(self) -> dict[str, str | None]:
        return {"name": self.name, "brand": self.brand, "mpn": self.mpn, "gtin": self.gtin}


# ---------------------------------------------------------------------------- helpers


def parse_price(value: Any) -> float | None:
    """Parses '1299.00', 1299, '1.299,00 €', '$1,299.99', '49,90'."""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return float(value) if value > 0 else None
    text = re.sub(r"[^\d.,]", "", str(value))
    if not text or not any(ch.isdigit() for ch in text):
        return None
    if "," in text and "." in text:
        decimal_sep = "," if text.rfind(",") > text.rfind(".") else "."
        thousands_sep = "." if decimal_sep == "," else ","
        text = text.replace(thousands_sep, "").replace(decimal_sep, ".")
    elif sep := ("," if "," in text else "." if "." in text else None):
        whole, _, frac = text.rpartition(sep)
        if len(frac) == 3 and whole:  # "1,299" / "1.299" / "1.299.000" — thousands separators
            text = text.replace(sep, "")
        else:  # "49,90" / "49.9" — decimal separator
            text = whole.replace(sep, "") + "." + frac
    try:
        price = float(Decimal(text))
    except InvalidOperation:
        return None
    return price if price > 0 else None


def normalize_gtin(value: Any) -> str | None:
    digits = re.sub(r"\D", "", str(value or ""))
    if not 8 <= len(digits) <= 14:
        return None
    return digits.lstrip("0") or None  # GTIN-13 "04006381333931" == GTIN-14 "4006381333931"


def normalize_code(value: Any) -> str | None:
    code = re.sub(r"[^a-z0-9]", "", str(value or "").lower())
    return code or None


def _availability(value: Any) -> bool | None:
    key = str(value or "").lower().rstrip("/").rsplit("/", 1)[-1]
    if key in IN_STOCK:
        return True
    if key in OUT_OF_STOCK:
        return False
    return None


def _text(value: Any) -> str | None:
    if isinstance(value, list):
        value = value[0] if value else None
    if isinstance(value, dict):
        value = value.get("name") or value.get("url") or value.get("contentUrl")
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _url_key(url: str) -> str:
    """Compares URLs ignoring scheme, "www." and a trailing slash (but not the query:
    variants of one product often differ only by `?size=42`)."""
    parts = urlsplit(url)
    host = parts.netloc.lower().removeprefix("www.")
    return f"{host}{parts.path.rstrip('/')}?{parts.query}"


# ---------------------------------------------------------------------------- JSON-LD


def _types(node: dict) -> set[str]:
    raw = node.get("@type")
    values = raw if isinstance(raw, list) else [raw]
    return {str(v).lower().rsplit("/", 1)[-1] for v in values if v}


def _walk(data: Any):
    if isinstance(data, list):
        for item in data:
            yield from _walk(item)
    elif isinstance(data, dict):
        yield data
        for key, value in data.items():
            if key != "offers" and isinstance(value, dict | list):
                yield from _walk(value)


def _offers_of(node: dict) -> list[dict]:
    offers: list[dict] = []
    raw = node.get("offers")
    for offer in raw if isinstance(raw, list) else [raw]:
        if not isinstance(offer, dict):
            continue
        offers.append(offer)
        nested = offer.get("offers")  # AggregateOffer may list individual offers
        if isinstance(nested, list):
            offers.extend(o for o in nested if isinstance(o, dict))
    for variant in node.get("hasVariant") or []:
        if isinstance(variant, dict):
            offers.extend(_offers_of(variant))
    return offers


def _offer_price(offer: dict) -> tuple[float | None, str | None]:
    price = parse_price(offer.get("price")) or parse_price(offer.get("lowPrice"))
    currency = offer.get("priceCurrency")
    spec = offer.get("priceSpecification")
    for item in spec if isinstance(spec, list) else [spec]:
        if isinstance(item, dict):
            price = price or parse_price(item.get("price"))
            currency = currency or item.get("priceCurrency")
    return price, (str(currency).upper() if currency else None)


def _from_jsonld(soup: BeautifulSoup, page_url: str) -> ProductData | None:
    products: list[dict] = []
    for script in soup.find_all("script", attrs={"type": re.compile(r"ld\+json", re.I)}):
        raw = (script.string or script.get_text() or "").strip()
        try:
            data = json.loads(raw, strict=False)
        except ValueError:
            continue
        products.extend(node for node in _walk(data) if _types(node) & PRODUCT_TYPES)
    if not products:
        return None

    target = _url_key(page_url)
    best: tuple[dict, dict | None, float | None, str | None] | None = None
    for product in products:
        priced = [(o, *_offer_price(o)) for o in _offers_of(product)]
        priced = [p for p in priced if p[1]]
        if not priced:
            best = best or (product, None, None, None)
            continue
        same_url = [p for p in priced if p[0].get("url") and _url_key(p[0]["url"]) == target]
        in_stock = [p for p in priced if _availability(p[0].get("availability")) is not False]
        offer, price, currency = (same_url or [min(in_stock or priced, key=lambda p: p[1])])[0]
        best = (product, offer, price, currency)
        break

    product, offer, price, currency = best
    data = ProductData(
        name=_text(product.get("name")),
        brand=_text(product.get("brand")),
        mpn=_text(product.get("mpn")) or _text(product.get("model")),
        gtin=next(
            (
                _text(product.get(key))
                for key in ("gtin13", "gtin", "gtin12", "gtin14", "gtin8", "isbn")
                if product.get(key)
            ),
            None,
        ),
        image=_text(product.get("image")),
    )
    if offer is not None:
        data.price, data.currency = price, currency
        data.in_stock = _availability(offer.get("availability"))
        data.method = "jsonld"
        shown = {
            k: offer[k]
            for k in ("@type", "price", "lowPrice", "priceCurrency", "availability", "url")
            if k in offer
        }
        data.evidence = json.dumps(shown, ensure_ascii=False)[:400]
    return data


# ---------------------------------------------------------------- microdata & meta tags


def _attr_or_text(tag) -> str | None:
    if tag is None:
        return None
    return tag.get("content") or tag.get("href") or tag.get_text(" ", strip=True) or None


def _from_microdata(soup: BeautifulSoup) -> ProductData | None:
    price_tag = soup.select_one('[itemprop="price"]')
    price = parse_price(_attr_or_text(price_tag))
    if not price:
        return None
    scope = price_tag.find_parent(attrs={"itemtype": re.compile("Product", re.I)}) or soup
    currency = _attr_or_text(scope.select_one('[itemprop="priceCurrency"]'))
    return ProductData(
        name=_attr_or_text(scope.select_one('[itemprop="name"]')),
        brand=_attr_or_text(scope.select_one('[itemprop="brand"]')),
        price=price,
        currency=currency.upper() if currency else None,
        in_stock=_availability(_attr_or_text(scope.select_one('[itemprop="availability"]'))),
        method="microdata",
        evidence=str(price_tag)[:300],
    )


def _meta(soup: BeautifulSoup, *names: str) -> str | None:
    for name in names:
        tag = soup.find("meta", attrs={"property": name}) or soup.find("meta", attrs={"name": name})
        if tag and tag.get("content"):
            return tag["content"].strip()
    return None


def _from_meta(soup: BeautifulSoup) -> ProductData | None:
    price = parse_price(_meta(soup, "product:price:amount", "og:price:amount"))
    if not price:
        return None
    currency = _meta(soup, "product:price:currency", "og:price:currency")
    availability = _meta(soup, "product:availability", "og:availability")
    return ProductData(
        name=_meta(soup, "og:title"),
        price=price,
        currency=currency.upper() if currency else None,
        in_stock=None if availability is None else "in" in availability.lower(),
        method="meta",
        evidence=f'<meta property="product:price:amount" content="{price}"> currency={currency}',
    )


def extract_structured(html: str, page_url: str) -> ProductData:
    soup = BeautifulSoup(html, "html.parser")
    data = _from_jsonld(soup, page_url) or ProductData()
    if not data.has_price:
        fallback = _from_microdata(soup) or _from_meta(soup)
        if fallback:
            for field in ("price", "currency", "in_stock", "method", "evidence"):
                setattr(data, field, getattr(fallback, field))
            data.name = data.name or fallback.name
            data.brand = data.brand or fallback.brand
    data.name = data.name or _meta(soup, "og:title")
    data.image = data.image or _meta(soup, "og:image")
    return data


# ------------------------------------------------------------------------ LLM fallback


def _squash(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def quote_supports_price(page_text: str, quote: str | None, price: float | None) -> bool:
    """The model's quote must literally appear on the page and contain the price digits."""
    if not quote or not price:
        return False
    if _squash(quote) not in _squash(page_text):
        return False
    digits = re.sub(r"\D", "", quote)
    whole = str(int(price))
    return whole in digits


async def read_product_data(page: Page, *, usage: llm.UsageSink | None = None) -> ProductData:
    data = extract_structured(page.html, page.url) if page.html else ProductData()
    if data.has_price and data.name:
        return data
    if not get_settings().llm_configured:
        data.note = data.note or "No structured price data on the page and AI reading is off."
        return data

    result = await llm.extract_product(page.text, page.url, usage=usage)
    data.name = data.name or result.name
    data.brand = data.brand or result.brand
    data.mpn = data.mpn or result.mpn
    data.gtin = data.gtin or result.gtin
    if data.has_price:
        return data
    if not result.is_product_page:
        data.note = "This doesn't look like a single product page."
    elif result.price and result.currency:
        if quote_supports_price(page.text, result.price_quote, result.price):
            data.price, data.currency = result.price, result.currency.upper()
            data.in_stock = result.in_stock
            data.method = "llm"
            data.evidence = result.price_quote or ""
        else:
            data.note = "The AI-read price could not be verified against the page text."
    else:
        data.note = "No price found on the page."
    return data
