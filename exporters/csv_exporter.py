import csv
from typing import Any


def save_products_to_csv(
    products: list[dict[str, Any]],
    output_file: str,
) -> None:
    fieldnames = [
        "id",
        "title",
        "category",
        "brand",
        "price",
        "discountPercentage",
        "rating",
        "stock",
    ]

    with open(
        output_file,
        mode="w",
        newline="",
        encoding="utf-8",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(products)