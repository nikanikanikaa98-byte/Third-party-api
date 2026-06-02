from typing import Any


def generate_report(
    total_products: int,
    valid_products: list[dict[str, Any]],
    invalid_products: list[dict[str, Any]],
    suspicious_products: list[dict[str, Any]],
    low_stock_products: list[dict[str, Any]],
    average_price: float,
    top_expensive_products: list[dict[str, Any]],
) -> str:
    report_lines = [
        "# Products Report",
        "",
        f"Total products fetched: {total_products}",
        f"Valid products count: {len(valid_products)}",
        (
            "Invalid or suspicious products count: "
            f"{len(invalid_products) + len(suspicious_products)}"
        ),
        f"Average price: {average_price:.2f}",
        f"Products with low stock: {len(low_stock_products)}",
        "",
        "## Top 5 Most Expensive Products",
    ]

    for product in top_expensive_products:
        report_lines.append(
            (
                f"- {product['title']} "
                f"(${product['price']})"
            )
        )

    report_lines.append("")
    report_lines.append("## Low Stock Products")

    for product in low_stock_products:
        report_lines.append(
            (
                f"- {product['title']} "
                f"(stock: {product['stock']})"
            )
        )

    return "\n".join(report_lines)