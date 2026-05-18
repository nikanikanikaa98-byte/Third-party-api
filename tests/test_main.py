import pytest

from main import (
    calculate_average_price,
    fetch_products,
    normalize_product,
    validate_product,
)


class FakeResponse:
    def __init__(self, status_code, payload=None, json_error=False):
        self.status_code = status_code
        self.payload = payload
        self.json_error = json_error

    def json(self):
        if self.json_error:
            raise ValueError("Invalid JSON")
        return self.payload


def test_normalize_product_keeps_required_fields():
    raw_product = {
        "id": 1,
        "title": "Test Product",
        "category": "test",
        "brand": "Test Brand",
        "price": 10.5,
        "discountPercentage": 5,
        "rating": 4.5,
        "stock": 12,
        "extraField": "not needed",
    }

    normalized = normalize_product(raw_product)

    assert normalized == {
        "id": 1,
        "title": "Test Product",
        "category": "test",
        "brand": "Test Brand",
        "price": 10.5,
        "discountPercentage": 5,
        "rating": 4.5,
        "stock": 12,
    }


def test_validate_product_accepts_valid_product():
    product = {
        "id": 1,
        "title": "Valid Product",
        "category": "test",
        "brand": "",
        "price": 10,
        "discountPercentage": 5,
        "rating": 4,
        "stock": 3,
    }

    assert validate_product(product) == []


def test_validate_product_rejects_invalid_product():
    product = {
        "id": None,
        "title": "",
        "category": "test",
        "brand": "",
        "price": -10,
        "discountPercentage": 5,
        "rating": 8,
        "stock": -1,
    }

    issues = validate_product(product)

    assert "id must exist" in issues
    assert "title must not be empty" in issues
    assert "price must be a positive number" in issues
    assert "rating must be between 0 and 5" in issues
    assert "stock must not be negative" in issues


def test_calculate_average_price():
    products = [
        {"price": 10},
        {"price": 20},
        {"price": 30},
    ]

    assert calculate_average_price(products) == 20


def test_fetch_products_accepts_valid_response(monkeypatch):
    def fake_get(api_url, params, timeout):
        return FakeResponse(
            status_code=200,
            payload={
                "products": [
                    {
                        "id": 1,
                        "title": "Test Product",
                        "category": "test",
                        "price": 10,
                        "discountPercentage": 1,
                        "rating": 4,
                        "stock": 5,
                    }
                ]
            },
        )

    monkeypatch.setattr("main.requests.get", fake_get)

    products = fetch_products(
        api_url="https://example.com/products",
        limit=10,
        skip=None,
        timeout=5,
        retries=0,
    )

    assert len(products) == 1
    assert products[0]["id"] == 1


def test_fetch_products_rejects_invalid_json(monkeypatch):
    def fake_get(api_url, params, timeout):
        return FakeResponse(status_code=200, json_error=True)

    monkeypatch.setattr("main.requests.get", fake_get)

    with pytest.raises(RuntimeError, match="API returned invalid JSON"):
        fetch_products(
            api_url="https://example.com/products",
            limit=None,
            skip=None,
            timeout=5,
            retries=0,
        )


def test_fetch_products_rejects_empty_product_list(monkeypatch):
    def fake_get(api_url, params, timeout):
        return FakeResponse(
            status_code=200,
            payload={"products": []},
        )

    monkeypatch.setattr("main.requests.get", fake_get)

    with pytest.raises(RuntimeError, match="API returned an empty product list"):
        fetch_products(
            api_url="https://example.com/products",
            limit=None,
            skip=None,
            timeout=5,
            retries=0,
        )