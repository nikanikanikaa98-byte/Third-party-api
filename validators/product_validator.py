from typing import Any


def is_number(value: Any) -> bool:
    return isinstance(value, int | float)


def validate_product(product: dict[str, Any]) -> list[str]:
    errors = []

    if product.get("id") is None:
        errors.append("Missing product id.")

    title = product.get("title")

    if not isinstance(title, str) or not title.strip():
        errors.append("Missing or empty title.")

    price = product.get("price")

    if not is_number(price) or price <= 0:
        errors.append("Price must be a positive number.")

    rating = product.get("rating")

    if not is_number(rating) or not 0 <= rating <= 5:
        errors.append("Rating must be between 0 and 5.")

    stock = product.get("stock")

    if not isinstance(stock, int) or stock < 0:
        errors.append("Stock must not be negative.")

    required_fields = [
        "id",
        "title",
        "category",
        "price",
        "discountPercentage",
        "rating",
        "stock",
    ]

    missing_fields = [
        field
        for field in required_fields
        if field not in product
    ]

    if missing_fields:
        errors.append(
            "Missing required fields: "
            + ", ".join(missing_fields)
        )

    return errors