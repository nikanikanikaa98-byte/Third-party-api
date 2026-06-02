# Third-Party API Integration Utility

## Short Project Summary

This project is a Python command-line utility that integrates with the public DummyJSON Products API:

https://dummyjson.com/products

The utility fetches product data, normalizes selected fields, validates product records, detects invalid or suspicious entries, saves cleaned data to a CSV file, stores data into a local SQLite database, and generates a Markdown report.

The project also supports multiple connectors via a Factory pattern, allowing switching between real and mock data sources.

---

# Architecture Overview

The project is structured as a small integration pipeline:

API / Mock Connector
        ↓
   Normalization
        ↓
   Validation Layer
        ↓
   Service Layer (business logic)
        ↓
 CSV Export + SQLite Storage
        ↓
   Report Generation

Key design patterns used:
- Factory Pattern (connector creation)
- Repository Pattern (database abstraction)
- Service Layer (business logic separation)
- Mock Connector (testing without external API)

---

# Run Instructions

## Create virtual environment
```
python -m venv .venv
```

## Activate (Windows PowerShell)
```
.\.venv\Scripts\Activate.ps1
```

## Install dependencies
```
pip install -r requirements.txt
```
---

# Run
```
python main.py --connector dummyjson
```
```
python main.py --connector mock
```
---

# Output Files

- cleaned_products.csv
- report.md
- database/products.db

---

# AI Tools Disclosure

ChatGPT assisted in architecture design, debugging, and documentation.
