from typing import Any

from validators.product_validator import validate_product


class ProductService:

    @staticmethod
    def normalize_product(product: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": product.get("id"),
            "title": product.get("title"),
            "category": product.get("category"),
            "brand": product.get("brand", ""),
            "price": product.get("price"),
            "discountPercentage": product.get("discountPercentage"),
            "rating": product.get("rating"),
            "stock": product.get("stock"),
        }

    @staticmethod
    def calculate_average_price(
        products: list[dict[str, Any]]
    ) -> float:

        if not products:
            return 0.0

        total_price = sum(
            product["price"] for product in products
        )

        return total_price / len(products)

    @staticmethod
    def process_products(
        products: list[dict[str, Any]],
        low_stock_threshold: int,
    ) -> dict[str, Any]:

        normalized_products = []
        valid_products = []
        invalid_products = []
        validation_errors = []

        for index, product in enumerate(products):

            if not isinstance(product, dict):

                invalid_products.append(
                    {"raw_value": product}
                )

                validation_errors.append(
                    {
                        "index": index,
                        "id": None,
                        "title": None,
                        "issues": [
                            "Product record is not an object"
                        ],
                    }
                )

                continue

            normalized_product = (
                ProductService.normalize_product(product)
            )

            issues = validate_product(normalized_product)

            normalized_products.append(normalized_product)

            if issues:

                invalid_products.append(
                    normalized_product
                )

                validation_errors.append(
                    {
                        "index": index,
                        "id": normalized_product.get("id"),
                        "title": normalized_product.get("title"),
                        "issues": issues,
                    }
                )

            else:
                valid_products.append(
                    normalized_product
                )

        low_stock_products = [
            product
            for product in valid_products
            if product["stock"] <= low_stock_threshold
        ]

        top_expensive_products = sorted(
            valid_products,
            key=lambda product: product["price"],
            reverse=True,
        )[:5]

        average_price = (
            ProductService.calculate_average_price(
                valid_products
            )
        )

        invalid_or_suspicious_count = (
            len(invalid_products)
            + len(low_stock_products)
        )

        return {
            "normalized_products": normalized_products,
            "valid_products": valid_products,
            "invalid_products": invalid_products,
            "validation_errors": validation_errors,
            "low_stock_products": low_stock_products,
            "top_expensive_products": top_expensive_products,
            "average_price": average_price,
            "invalid_or_suspicious_count": (
                invalid_or_suspicious_count
            ),
        }