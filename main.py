import argparse
import csv
import sys
from datetime import datetime

import requests


API_URL = "https://dummyjson.com/products"
OUTPUT_FILE = "cleaned_products.csv"
REPORT_FILE = "report.md"
LOW_STOCK_THRESHOLD = 5
TIMEOUT_SECONDS = 10

SELECTED_FIELDS = [
    "id",
    "title",
    "category",
    "brand",
    "price",
    "discountPercentage",
    "rating",
    "stock",
]


def fetch_products(api_url, limit, timeout):
    params = {}

    if limit is not None:
        params["limit"] = limit

    try:
        response = requests.get(api_url, params=params, timeout=timeout)
    except requests.exceptions.Timeout:
        raise RuntimeError(f"Request timed out after {TIMEOUT_SECONDS} seconds.")
    except requests.exceptions.ConnectionError:
        raise RuntimeError("Could not connect to the API. The service may be unavailable.")
    except requests.exceptions.RequestException as error:
        raise RuntimeError(f"Unexpected request error: {error}")

    if response.status_code != 200:
        raise RuntimeError(f"API returned non-200 status code: {response.status_code}")

    try:
        data = response.json()
    except ValueError:
        raise RuntimeError("API returned invalid JSON.")

    if not isinstance(data, dict):
        raise RuntimeError("Unexpected API response format: root response is not an object.")

    if "products" not in data:
        raise RuntimeError("Unexpected API response format: missing 'products' field.")

    products = data["products"]

    if not isinstance(products, list):
        raise RuntimeError("Unexpected API response format: 'products' is not a list.")

    if len(products) == 0:
        raise RuntimeError("API returned an empty product list.")

    return products


def normalize_product(product):
    normalized = {
        "id": product.get("id"),
        "title": product.get("title"),
        "category": product.get("category"),
        "brand": product.get("brand", ""),
        "price": product.get("price"),
        "discountPercentage": product.get("discountPercentage"),
        "rating": product.get("rating"),
        "stock": product.get("stock"),
    }

    return normalized


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def validate_product(product):
    issues = []

    required_fields = [
        "id",
        "title",
        "category",
        "price",
        "discountPercentage",
        "rating",
        "stock",
    ]

    for field in required_fields:
        if field not in product:
            issues.append(f"Missing required field: {field}")

    product_id = product.get("id")
    title = product.get("title")
    price = product.get("price")
    rating = product.get("rating")
    stock = product.get("stock")

    if product_id is None:
        issues.append("id must exist")

    if title is None or str(title).strip() == "":
        issues.append("title must not be empty")

    if not is_number(price):
        issues.append("price must be a number")
    elif price <= 0:
        issues.append("price must be a positive number")

    if not is_number(rating):
        issues.append("rating must be a number")
    elif rating < 0 or rating > 5:
        issues.append("rating must be between 0 and 5")

    if not is_number(stock):
        issues.append("stock must be a number")
    elif stock < 0:
        issues.append("stock must not be negative")

    return issues


def save_products_to_csv(products, output_file):
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=SELECTED_FIELDS)
        writer.writeheader()
        writer.writerows(products)


def calculate_average_price(products):
    if not products:
        return 0

    total_price = 0

    for product in products:
        total_price += product["price"]

    average_price = total_price / len(products)

    return average_price


def generate_report(
    report_file,
    total_fetched,
    valid_products,
    invalid_products,
    validation_errors,
    low_stock_products,
    top_expensive_products,
    average_price,
    invalid_or_suspicious_count,
    output_file,
    low_stock_threshold,
):
    report_lines = [
        "# Third-Party API Integration Report",
        "",
        f"Generated at: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Summary",
        "",
        f"- Total products fetched: {total_fetched}",
        f"- Valid products count: {len(valid_products)}",
        f"- Invalid products count: {len(invalid_products)}",
        f"- Invalid or suspicious products count: {invalid_or_suspicious_count}",
        f"- Average price: {average_price:.2f}",
        f"- Low stock threshold: <= {low_stock_threshold}",
        f"- Low stock products count: {len(low_stock_products)}",
        f"- Cleaned output file: `{output_file}`",
        "",
        "## Products With Low Stock",
        "",
    ]

    if low_stock_products:
        for product in low_stock_products:
            report_lines.append(
                f"- ID {product['id']}: {product['title']} | stock: {product['stock']} | price: {product['price']}"
            )
    else:
        report_lines.append("No low stock products found.")

    report_lines.extend(
        [
            "",
            "## Top 5 Most Expensive Products",
            "",
        ]
    )

    if top_expensive_products:
        for index, product in enumerate(top_expensive_products, start=1):
            report_lines.append(
                f"{index}. ID {product['id']}: {product['title']} | price: {product['price']} | category: {product['category']}"
            )
    else:
        report_lines.append("No valid products available for ranking.")

    report_lines.extend(
        [
            "",
            "## Validation Errors",
            "",
        ]
    )

    if validation_errors:
        for error in validation_errors:
            issues_text = ", ".join(error["issues"])
            report_lines.append(
                f"- Product index {error['index']} | ID: {error['id']} | Title: {error['title']} | Issues: {issues_text}"
            )
    else:
        report_lines.append("No validation errors found.")

    report_lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Low stock products are treated as suspicious but not invalid.",
            "- Average price is calculated using valid products only.",
            "- Brand is optional and is saved as an empty value if missing.",
            "- The utility expects the API response to contain a `products` list.",
        ]
    )

    with open(report_file, mode="w", encoding="utf-8") as file:
        file.write("\n".join(report_lines))

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Fetch, normalize, validate, and report product data from DummyJSON Products API."
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Number of products to fetch. Example: --limit 50",
    )

    parser.add_argument(
        "--output",
        default=OUTPUT_FILE,
        help=f"Output CSV file. Default: {OUTPUT_FILE}",
    )

    parser.add_argument(
        "--report",
        default=REPORT_FILE,
        help=f"Report Markdown file. Default: {REPORT_FILE}",
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=TIMEOUT_SECONDS,
        help=f"Request timeout in seconds. Default: {TIMEOUT_SECONDS}",
    )

    parser.add_argument(
        "--low-stock-threshold",
        type=int,
        default=LOW_STOCK_THRESHOLD,
        help=f"Stock value considered low. Default: {LOW_STOCK_THRESHOLD}",
    )

    return parser.parse_args()
args = parse_arguments()

try:
    products = fetch_products(
        api_url=API_URL,
        limit=args.limit,
        timeout=args.timeout,
    )
except RuntimeError as error:
    print(f"Error: {error}")
    sys.exit(1)

print("Total products received:", len(products))

normalized_products = []
valid_products = []
invalid_products = []
validation_errors = []

for index, product in enumerate(products):
    normalized_product = normalize_product(product)
    issues = validate_product(normalized_product)

    normalized_products.append(normalized_product)

    if issues:
        invalid_products.append(normalized_product)
        validation_errors.append(
            {
                "index": index,
                "id": normalized_product.get("id"),
                "title": normalized_product.get("title"),
                "issues": issues,
            }
        )
    else:
        valid_products.append(normalized_product)

low_stock_products = []

for product in valid_products:
    if product["stock"] <= args.low_stock_threshold:
        low_stock_products.append(product)

top_expensive_products = sorted(
    valid_products,
    key=lambda product: product["price"],
    reverse=True,
)[:5]

average_price = calculate_average_price(valid_products)

invalid_or_suspicious_count = len(invalid_products) + len(low_stock_products)

print("Normalized products count:", len(normalized_products))
print("Valid products count:", len(valid_products))
print("Invalid products count:", len(invalid_products))
print("Invalid or suspicious products count:", invalid_or_suspicious_count)
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
        print(product["id"], product["title"], "stock:", product["stock"])
else:
    print("No low stock products found.")

save_products_to_csv(normalized_products, args.output)

generate_report(
    report_file=args.report,
    total_fetched=len(products),
    valid_products=valid_products,
    invalid_products=invalid_products,
    validation_errors=validation_errors,
    low_stock_products=low_stock_products,
    top_expensive_products=top_expensive_products,
    average_price=average_price,
    invalid_or_suspicious_count=invalid_or_suspicious_count,
    output_file=args.output,
    low_stock_threshold=args.low_stock_threshold,
)

print()
print(f"Saved cleaned products to {args.output}")
print(f"Saved report to {args.report}")