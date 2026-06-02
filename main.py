import argparse
import logging
import sys
from repositories.product_repository import ProductRepository
from services.product_service import ProductService

from connectors.dummyjson_connector import DummyJsonConnector
from connectors.connector_factory import ConnectorFactory
from exporters.csv_exporter import save_products_to_csv
from reports.report_generator import generate_report


DEFAULT_API_URL = "https://dummyjson.com/products"
DEFAULT_OUTPUT_FILE = "cleaned_products.csv"
DEFAULT_REPORT_FILE = "report.md"
DEFAULT_LOW_STOCK_THRESHOLD = 5
DEFAULT_TIMEOUT_SECONDS = 10
DEFAULT_RETRIES = 2


def configure_logging(verbose: bool) -> None:
    log_level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        level=log_level,
        format="%(levelname)s: %(message)s",
    )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch, normalize, validate, and report "
            "product data from DummyJSON Products API."
        )
    )

    parser.add_argument(
        "--api-url",
        default=DEFAULT_API_URL,
        help=f"Products API URL. Default: {DEFAULT_API_URL}",
    )
    parser.add_argument(
        "--connector",
        default="dummyjson",
        help="Connector type: dummyjson or mock",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Number of products to fetch. Example: --limit 50",
    )

    parser.add_argument(
        "--skip",
        type=int,
        default=None,
        help="Number of products to skip. Example: --skip 50",
    )

    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT_FILE,
        help=f"Output CSV file. Default: {DEFAULT_OUTPUT_FILE}",
    )

    parser.add_argument(
        "--report",
        default=DEFAULT_REPORT_FILE,
        help=f"Report Markdown file. Default: {DEFAULT_REPORT_FILE}",
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=(
            "Request timeout in seconds. "
            f"Default: {DEFAULT_TIMEOUT_SECONDS}"
        ),
    )

    parser.add_argument(
        "--retries",
        type=int,
        default=DEFAULT_RETRIES,
        help=(
            "Number of retry attempts for temporary "
            f"request failures. Default: {DEFAULT_RETRIES}"
        ),
    )

    parser.add_argument(
        "--low-stock-threshold",
        type=int,
        default=DEFAULT_LOW_STOCK_THRESHOLD,
        help=(
            "Stock value considered low. "
            f"Default: {DEFAULT_LOW_STOCK_THRESHOLD}"
        ),
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable detailed logging output.",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_arguments()
    
    repository = ProductRepository("database/products.db")
    repository.create_table()

    configure_logging(args.verbose)

    if args.limit is not None and args.limit < 0:
        print("Error: --limit must not be negative.")
        return 1

    if args.skip is not None and args.skip < 0:
        print("Error: --skip must not be negative.")
        return 1

    if args.timeout <= 0:
        print("Error: --timeout must be greater than 0.")
        return 1

    if args.retries < 0:
        print("Error: --retries must not be negative.")
        return 1

    try:
        connector = ConnectorFactory.create(
            connector_type=args.connector,
            api_url=args.api_url,
            limit=args.limit,
            skip=args.skip,
            timeout=args.timeout,
            retries=args.retries,
        )

        products = connector.fetch_products()

    except RuntimeError as error:
        print(f"Error: {error}")
        return 1

    print("Total products received:", len(products))

    processed_data = ProductService.process_products(
    products=products,
    low_stock_threshold=args.low_stock_threshold,
    )

    normalized_products = processed_data["normalized_products"]

    valid_products = processed_data["valid_products"]

    invalid_products = processed_data["invalid_products"]

    validation_errors = processed_data["validation_errors"]

    low_stock_products = processed_data["low_stock_products"]

    top_expensive_products = processed_data[
    "top_expensive_products"
    ]

    average_price = processed_data["average_price"]

    invalid_or_suspicious_count = processed_data[
    "invalid_or_suspicious_count"
    ]

    print("Normalized products count:", len(normalized_products))
    print("Valid products count:", len(valid_products))
    print("Invalid products count:", len(invalid_products))
    print(
        "Invalid or suspicious products count:",
        invalid_or_suspicious_count,
    )
    print("Average price:", round(average_price, 2))
    print("Low stock products count:", len(low_stock_products))

    if validation_errors:
        print()
        print("Validation errors:")

        for error in validation_errors:
            print(error)
    else:
        print()
        print("No validation errors found.")

    print()
    print("Top 5 most expensive products:")

    for product in top_expensive_products:
        print(product["id"], product["title"], product["price"])

    print()
    print("Products with low stock:")

    if low_stock_products:
        for product in low_stock_products:
            print(
                product["id"],
                product["title"],
                "stock:",
                product["stock"],
            )
    else:
        print("No low stock products found.")

    repository.save_products(valid_products)

    save_products_to_csv(valid_products, args.output)

    report_text = generate_report(
        total_products=len(products),
        valid_products=valid_products,
        invalid_products=invalid_products,
        suspicious_products=low_stock_products,
        low_stock_products=low_stock_products,
        average_price=average_price,
        top_expensive_products=top_expensive_products,
    )

    with open(args.report, mode="w", encoding="utf-8") as file:
        file.write(report_text)

    print()
    print(f"Saved cleaned products to {args.output}")
    print(f"Saved report to {args.report}")
    
    products_from_db = repository.get_all_products()

    low_stock_from_db = repository.get_low_stock_products(5)

    print()
    print("Low stock products from database:")
    print("Count:", len(low_stock_from_db))

    print()
    print("Products stored in database:")
    print("Count:", len(products_from_db))

    return 0


if __name__ == "__main__":
    sys.exit(main())