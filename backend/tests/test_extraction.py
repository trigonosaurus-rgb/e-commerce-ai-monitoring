import pytest

from backend.extraction import (
    extract_structured,
    normalize_gtin,
    parse_price,
    quote_supports_price,
)
from backend.tests.conftest import fixture_html


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("1299.00", 1299.0),
        (1299, 1299.0),
        ("1.299,00 €", 1299.0),
        ("$1,299.99", 1299.99),
        ("49,90", 49.9),
        ("1,299", 1299.0),
        ("1.299", 1299.0),
        ("0", None),
        ("free", None),
        (None, None),
        (True, None),
    ],
)
def test_parse_price(raw, expected):
    assert parse_price(raw) == expected


def test_gtin_normalization_ignores_leading_zeros():
    assert normalize_gtin("0017817846318") == normalize_gtin("17817846318")
    assert normalize_gtin("12345") is None


def test_jsonld_offer():
    data = extract_structured(
        fixture_html("jsonld_offer.html"), "https://www.example-audio.de/sony-wh-1000xm6"
    )
    assert data.name.startswith("Sony WH-1000XM6")
    assert data.brand == "Sony"
    assert data.gtin == "4548736160213"
    assert (data.price, data.currency, data.in_stock, data.method) == (399.0, "EUR", True, "jsonld")
    assert '"price": "399.00"' in data.evidence


def test_jsonld_graph_with_aggregate_offer():
    data = extract_structured(
        fixture_html("jsonld_graph_aggregate.html"), "https://shop.example.com/qc"
    )
    assert data.name == "Bose QuietComfort Ultra Headphones"
    assert (data.price, data.currency, data.in_stock) == (1299.0, "SEK", False)


def test_product_group_prefers_variant_from_url():
    html = fixture_html("product_group_variants.html")
    exact = extract_structured(html, "https://shoes.example.com/trail-runner-3?size=42")
    assert exact.price == 149.95 and exact.in_stock is False
    # without a matching variant URL: the cheapest in-stock variant
    generic = extract_structured(html, "https://shoes.example.com/trail-runner-3")
    assert generic.price == 139.95 and generic.in_stock is True


def test_microdata():
    data = extract_structured(fixture_html("microdata.html"), "https://grinders.example.com/encore")
    assert (data.name, data.price, data.currency, data.method) == (
        "Baratza Encore ESP Coffee Grinder",
        199.95,
        "USD",
        "microdata",
    )


def test_meta_tags():
    data = extract_structured(fixture_html("meta_tags.html"), "https://lamps.example.com/nordic")
    assert (data.price, data.currency, data.method, data.in_stock) == (89.0, "GBP", "meta", True)
    assert data.name == "Nordic Desk Lamp, oak"


def test_page_without_structured_data_has_no_price():
    data = extract_structured(
        fixture_html("no_structured_data.html"), "https://clay.example.com/mug"
    )
    assert not data.has_price


def test_llm_quote_must_be_on_the_page():
    text = "Handmade ceramic mug\nPrice: 24,50 €\nShips within 3 days."
    assert quote_supports_price(text, "Price: 24,50 €", 24.5)
    assert not quote_supports_price(text, "Price: 19,90 €", 19.9)  # invented quote
    assert not quote_supports_price(text, "Ships within 3 days.", 24.5)  # quote without the price
