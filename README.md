# Third-Party API Integration Utility

## Short Project Summary

This project is a small Python command-line utility that integrates with the public DummyJSON Products API:

```text
https://dummyjson.com/products
```

The utility fetches product data, normalizes selected fields, validates product records, detects invalid or suspicious records, saves cleaned data to a CSV file, and generates a short Markdown report.

# Exact Run Instructions
1. Create a virtual environment
```text
python -m venv .venv
```

On Windows PowerShell, activate it:

```text
.\.venv\Scripts\Activate.ps1
```
2. Install dependencies
```text
pip install -r requirements.txt
```
3. Run the utility

Default run:

```text
python main.py
```

This generates:

cleaned_products.csv
report.md

## Optional run with custom arguments:

```text
python main.py --limit 50 --output products.csv --report custom_report.md
```

## Show available options:

```text
python main.py --help
```
## Used Libraries and Why They Were Chosen
- requests — used to make HTTP requests to the DummyJSON Products API.
- argparse — used to support command-line arguments such as --limit, --output, --report, --timeout, and --low-stock-threshold.
- csv — used to save normalized product data into a CSV file.
- datetime — used to add a generation timestamp to the report.
-- sys — used to exit the program gracefully when a critical error occurs.
## AI Tools Usage Disclosure

ChatGPT was used as an AI coding assistant during this assignment.

## AI assistance was used for:

- planning the implementation steps;
- explaining API integration logic;
- designing validation and error handling;
- drafting the Python code;
- drafting the part of README.

## My own implementation decisions included:

- using a Python CLI script;
- saving normalized data as CSV;
- generating a Markdown report;
- treating brand as optional;
- treating low stock as suspicious rather than invalid;
- adding command-line arguments for flexibility;
- Update and modify README.
## Validation Rules Implemented

The following validation rules are implemented:

- id must exist.
- title must not be empty.
- price must be a positive number.
- rating must be between 0 and 5.
- stock must not be negative.
- required fields are not silently ignored if missing.

The utility validates the following required fields:

- id
- title
- category
- price
- discountPercentage
- rating
- stock

## The brand field is optional because the assignment says brand if available.

Error Handling Implemented

## The utility handles the following failure cases:

- API unavailable or connection failure;

- request timeout;

- non-200 HTTP response;

- invalid JSON response;

- missing products field;

- unexpected response format;

- products field is not a list;

- empty product list;

- product-level missing or invalid fields.


If a critical API or response error occurs, the program prints a clear error message and exits gracefully.

### Example:

Error: API returned non-200 status code: 404
Assumptions and Tradeoffs
The API response is expected to contain a top-level products list.
Only the required selected fields are saved to the local CSV file.
brand is treated as optional.
Low stock products are treated as suspicious, not invalid.
Average price is calculated using valid products only.
CSV was chosen because it is simple and easy to inspect.
Markdown was chosen for the report because it is lightweight and readable.
The project is kept as a single Python file to match the scope of a small practical utility.
Automated tests were not included because they were optional.
What Could Go Wrong With This Third-Party API Integration in Real Life

Possible real-life integration risks include:

the API may become unavailable;
the API may become slow and cause timeouts;
the response format may change;
required fields may be removed or renamed;
field data types may change;
the API may return invalid or incomplete data;
the API may return invalid JSON;
pagination may be required for larger datasets;
rate limits may affect frequent requests;
duplicate product IDs may appear;
product data may become stale or inconsistent.
Future Improvements With More Time

Possible future improvements:

add automated tests with mocked API responses;
add retry logic for temporary API failures;
add structured logging;
add JSON output support;
add SQLite storage;
add duplicate ID detection;
add pagination with limit and skip;
add .env configuration support;
split the code into multiple modules;
add stronger type hints and schema validation.