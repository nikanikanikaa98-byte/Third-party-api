import pytest

from services.product_service import ProductService
from validators.product_validator import validate_product
from connectors.dummyjson_connector import DummyJsonConnector


class FakeResponse:
    def __init__(self, status_code, payload=None, json_error=False):
        self.status_code = status_code
        self.payload = payload
        self.json_error = json_error

    def json(self):
        if self.json_error:
            raise ValueError("Invalid JSON response received from API")
        return self.payload


# -----------------------------
# ProductService tests
# -----------------------------

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

    normalized = ProductService.normalize_product(raw_product)

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

    assert "Missing product id." in issues
    assert "Missing or empty title." in issues
    assert "Price must be a positive number." in issues
    assert "Rating must be between 0 and 5." in issues
    assert "Stock must not be negative." in issues


def test_calculate_average_price():
    products = [
        {"price": 10},
        {"price": 20},
        {"price": 30},
    ]

    assert ProductService.calculate_average_price(products) == 20


# -----------------------------
# DummyJsonConnector tests
# -----------------------------

def test_fetch_products_accepts_valid_response(monkeypatch):
    def fake_get(*args, **kwargs):
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

    monkeypatch.setattr(
        "connectors.dummyjson_connector.requests.get",
        fake_get,
    )

    connector = DummyJsonConnector(
        api_url="https://example.com/products",
        timeout=5,
        retries=0,
    )

    products = connector.fetch_products()

    assert len(products) == 1
    assert products[0]["id"] == 1


def test_fetch_products_rejects_invalid_json(monkeypatch):
    def fake_get(*args, **kwargs):
        return FakeResponse(status_code=200, json_error=True)

    monkeypatch.setattr(
        "connectors.dummyjson_connector.requests.get",
        fake_get,
    )

    connector = DummyJsonConnector(
        api_url="https://example.com/products",
        timeout=5,
        retries=0,
    )

    with pytest.raises(
        RuntimeError,
        match="Invalid JSON response received from API",
    ):
        connector.fetch_products()


def test_fetch_products_rejects_empty_product_list(monkeypatch):
    def fake_get(*args, **kwargs):
        return FakeResponse(
            status_code=200,
            payload={"products": []},
        )

    monkeypatch.setattr(
        "connectors.dummyjson_connector.requests.get",
        fake_get,
    )

    connector = DummyJsonConnector(
        api_url="https://example.com/products",
        timeout=5,
        retries=0,
    )

    with pytest.raises(
        RuntimeError,
        match="The API returned an empty product list.",
    ):
        connector.fetch_products()