# Sales Data Engineering Pipeline & Analytics Dashboard

**Python · pandas · SQL · SQLite · Streamlit · Medallion Architecture**

A beginner-friendly data engineering portfolio project that demonstrates how sales data can be ingested from CSV files, preserved in a raw layer, cleaned and validated, transformed into analytical tables, and presented through an interactive dashboard.

> **Project status:** Local implementation using SQLite. Snowflake and Kaggle dataset integration are optional extensions and should only be described as completed after you implement and test them.

---

## Table of Contents

- [Overview](#overview)
- [Objectives](#objectives)
- [Features](#features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [How the Pipeline Works](#how-the-pipeline-works)
- [Data Quality Rules](#data-quality-rules)
- [Database Tables](#database-tables)
- [Dashboard Features](#dashboard-features)
- [Prerequisites](#prerequisites)
- [Installation and Setup](#installation-and-setup)
- [Running the Project](#running-the-project)
- [Expected Output](#expected-output)
- [SQL Examples](#sql-examples)
- [Troubleshooting](#troubleshooting)
- [Limitations and Future Enhancements](#limitations-and-future-enhancements)
- [Resume Description](#resume-description)
- [Learning Outcomes](#learning-outcomes)
- [License](#license)

---

## Overview

This project implements a small end-to-end sales data pipeline. It reads sales transactions from a CSV file, stores the original records, validates and cleans the data, calculates revenue, creates analytical summaries with SQL, and displays the results in a Streamlit dashboard.

The project uses the **Bronze, Silver, and Gold** layers commonly associated with Medallion Architecture:

- **Bronze:** Raw source data preserved for traceability.
- **Silver:** Cleaned and validated records ready for analysis.
- **Gold:** Aggregated tables designed for business reporting.

The initial version uses a sample CSV and SQLite, allowing the complete workflow to run locally without a cloud account.

## Objectives

- Practice ingesting structured data from CSV files.
- Apply data cleansing and validation with Python and pandas.
- Understand the purpose of Bronze, Silver, and Gold data layers.
- Store raw and processed records in SQLite.
- Write SQL queries using grouping, aggregation, and sorting.
- Build an interactive dashboard for exploring sales metrics.
- Document a reproducible workflow suitable for a portfolio project.

## Features

### Data ingestion
- Reads a CSV file with pandas.
- Checks that expected columns exist.
- Stores source records in the Bronze table.

### Data cleaning and validation
- Trims whitespace from selected text fields.
- Converts dates and numeric fields to appropriate types.
- Rejects records with missing required values.
- Rejects non-positive quantities and negative unit prices.
- Exports rejected rows to a CSV file for review.
- Removes duplicate order IDs from the valid records.
- Calculates line revenue as `quantity × unit_price`.

### SQL analytics
- Creates a product-level summary.
- Creates a month-level sales summary.
- Calculates total revenue and counts for the pipeline report.

### Streamlit dashboard
Depending on the version of `dashboard.py` in your project, the dashboard can include:
- Revenue, order, units-sold, and average-order-value KPI cards.
- Date-range, category, and product filters.
- Monthly revenue trend chart.
- Revenue by product and category charts.
- Product performance and sales detail tables.
- Downloadable filtered sales data.
- Rejected-record and data-quality summaries.

## Architecture

```text
CSV Source
   |
   v
Python / pandas ingestion
   |
   v
BRONZE: bronze_sales
Original source rows
   |
   v
Validation and transformation
   |-----------------------> Rejected records CSV
   v
SILVER: silver_sales
Clean, valid, deduplicated records
   |
   v
SQL aggregations
   |-----------------------> GOLD: gold_product_sales
   |-----------------------> GOLD: gold_monthly_sales
   |
   v
Streamlit dashboard
KPIs, charts, filters, tables, downloads
```

This is a local demonstration of Medallion Architecture. It is not a distributed or production-grade data platform.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Pipeline orchestration and transformations |
| pandas | CSV ingestion, data cleaning, and validation |
| SQLite | Local relational database |
| SQL | Aggregations and analytical queries |
| Streamlit | Interactive dashboard |
| Git and GitHub | Version control and project sharing |
| VS Code | Development environment |

## Project Structure

The current working setup may keep the Python files in `output/`, as in the structure below. The path configuration in the provided scripts assumes `pipeline.py` and `dashboard.py` are in that folder.

```text
sales-data-pipeline/
├── data/
│   └── sales.csv
├── output/
│   ├── pipeline.py
│   ├── dashboard.py
│   ├── queries.sql
│   ├── sales.db                 # Generated when the pipeline runs
│   └── rejected_sales.csv       # Generated when the pipeline runs
├── venv/                        # Local virtual environment; do not commit
├── requirements.txt
├── README.md
└── .gitignore
```

Recommended long-term organization is to move `pipeline.py`, `dashboard.py`, and `queries.sql` into the project root, but if you do so, update the path definitions accordingly.

## How the Pipeline Works

### 1. Extract — CSV ingestion

The pipeline reads `data/sales.csv` using pandas. It initially reads values as strings so the original input values can be stored in the Bronze layer.

### 2. Bronze — raw data

The `bronze_sales` table stores the input CSV rows before the pipeline's cleaning transformations. This makes it possible to compare the original input with the cleaned output.

### 3. Silver — clean and validate

The pipeline:
1. Trims whitespace from key text columns.
2. Parses `order_date` as a date.
3. Converts `quantity` and `unit_price` to numeric values.
4. checks required fields for missing or blank values.
5. Rejects records with quantity less than or equal to zero.
6. Rejects records with negative unit prices.
7. Saves rejected rows to `output/rejected_sales.csv`.
8. Removes duplicate `order_id` values, keeping the first valid occurrence.
9. Standardizes dates and calculates `revenue`.

### 4. Gold — analytical tables

The pipeline creates two reporting tables:

- `gold_product_sales`: total units sold and total revenue by product and category.
- `gold_monthly_sales`: order counts and total revenue by month.

These tables are intended for dashboard reporting and SQL practice.

### 5. Visualize — Streamlit

The dashboard reads the cleaned Silver records and Gold summary tables from SQLite. It calculates KPIs and presents charts, tables, and data-quality information.

## Data Quality Rules

The sample pipeline applies these rules:

| Rule | Action |
|---|---|
| Required field missing or blank | Reject record |
| Date cannot be parsed | Reject record |
| Quantity is missing or not numeric | Reject record |
| Quantity is zero or negative | Reject record |
| Unit price is missing or not numeric | Reject record |
| Unit price is negative | Reject record |
| Duplicate order ID among valid rows | Keep first valid row; remove later duplicates |
| Valid record | Standardize date and calculate revenue |

**Important design note:** This starter project treats `order_id` as unique. In real sales systems, an order may contain multiple line items, so deduplication should instead use a transaction-line key when appropriate. The rules should be adapted to the source dataset.

## Database Tables

| Table / file | Layer | Description |
|---|---|---|
| `bronze_sales` | Bronze | Original CSV rows |
| `silver_sales` | Silver | Cleaned, validated, deduplicated records |
| `gold_product_sales` | Gold | Product/category sales summary |
| `gold_monthly_sales` | Gold | Monthly revenue and order summary |
| `rejected_sales.csv` | Quality output | Rows rejected by validation rules |
| `sales.db` | Database file | SQLite database containing pipeline tables |

## Dashboard Features

The dashboard can support the following analysis:

- **Total Revenue:** Sum of revenue for records matching the current filters.
- **Total Orders:** Count of unique order IDs in the filtered records.
- **Units Sold:** Sum of quantities in the filtered records.
- **Average Order Value:** Total revenue divided by unique orders.
- **Monthly Revenue Trend:** Revenue grouped by calendar month.
- **Product Performance:** Units sold, order count, and revenue by product/category.
- **Category Analysis:** Compare revenue across categories.
- **Sales Data Explorer:** Inspect filtered records.
- **CSV Export:** Download the currently filtered rows.
- **Data Quality Monitor:** Inspect rejected records and the valid-record rate.

The exact features depend on the dashboard code currently installed. Run the app and verify each feature before describing it as implemented.

## Prerequisites

Install the following:

- Python 3.10 or newer recommended.
- Visual Studio Code or another Python editor.
- Git (optional, for version control).
- A CSV file matching the schema below.

SQLite is included with Python. No separate database server is required.

### Required CSV columns

The starter pipeline expects these column names:

```text
order_id, order_date, product, category, quantity, unit_price, customer_id
```

Example:

```csv
order_id,order_date,product,category,quantity,unit_price,customer_id
1001,2026-01-05,Laptop,Electronics,2,55000,C001
1002,2026-01-08,Mouse,Accessories,5,500,C002
1003,2026-01-15,Keyboard,Accessories,3,1200,C003
```

The sample data may intentionally contain invalid rows for testing validation. Do not include real personal or confidential customer data in a public repository.

## Installation and Setup

### 1. Clone the repository or open the project folder

If you have already created the project locally, open that folder in VS Code.

### 2. Create a virtual environment

On Windows PowerShell, from the project root:

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can run Python directly through `venv\Scripts\python.exe` or use a terminal configured for your environment.

### 3. Install dependencies

Create `requirements.txt` with:

```text
pandas
streamlit
```

Then run:

```powershell
python -m pip install -r requirements.txt
```

### 4. Add the CSV

Place the source file at:

```text
data/sales.csv
```

Make sure its column names match the schema required by `pipeline.py`.

## Running the Project

The instructions below assume that `pipeline.py` and `dashboard.py` are inside the `output/` folder.

### 1. Open the terminal in the correct directory

```powershell
cd path\to\sales-data-pipeline\output
```

If the virtual environment is at the project root and is not active, activate it with:

```powershell
..\venv\Scripts\Activate.ps1
```

### 2. Run the data pipeline

```powershell
python pipeline.py
```

The script should:
- Read the source CSV.
- Recreate the Bronze and Silver tables.
- Generate the rejected-records CSV.
- Recreate the Gold analytical tables.
- Print a pipeline summary.

### 3. Run the dashboard

After the pipeline finishes successfully:

```powershell
streamlit run dashboard.py
```

Open the local URL shown in the terminal, commonly:

```text
http://localhost:8501
```

Keep the terminal running while you use the dashboard. Press `Ctrl+C` in the terminal to stop the Streamlit server.

## Expected Output

For the specific 13-row sample CSV described in the project tutorial, the expected report is approximately:

```text
Source records       : 13
Rejected records     : 2
Duplicates removed   : 1
Silver records       : 10
Total revenue        : 271,500.00
```

Your actual output depends on the CSV contents and validation rules. If you use an external Kaggle dataset, these sample counts and revenue figures will not apply.

## SQL Examples

You can run these queries using a SQLite database viewer or Python.

### 1. Product revenue

```sql
SELECT
    product,
    SUM(quantity) AS units_sold,
    ROUND(SUM(revenue), 2) AS total_revenue
FROM silver_sales
GROUP BY product
ORDER BY total_revenue DESC;
```

### 2. Monthly revenue

```sql
SELECT
    substr(order_date, 1, 7) AS sales_month,
    ROUND(SUM(revenue), 2) AS monthly_revenue
FROM silver_sales
GROUP BY substr(order_date, 1, 7)
ORDER BY sales_month;
```

### 3. Check for invalid records in Silver

```sql
SELECT *
FROM silver_sales
WHERE quantity <= 0
   OR unit_price < 0
   OR product IS NULL;
```

This query should return no rows for the validation rules used by the starter pipeline.

### 4. Compare Bronze and Silver counts

```sql
SELECT 'Bronze' AS layer, COUNT(*) AS record_count
FROM bronze_sales
UNION ALL
SELECT 'Silver' AS layer, COUNT(*) AS record_count
FROM silver_sales;
```

## Troubleshooting

### `FileNotFoundError: sales.csv`

Check that:
- The CSV is in the `data/` folder.
- The filename and extension are correct.
- `BASE_DIR` in `pipeline.py` points to the project root.

If `pipeline.py` is inside `output/`, the path configuration should be:

```python
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "sales.csv"
OUTPUT_DIR = BASE_DIR / "output"
DB_FILE = OUTPUT_DIR / "sales.db"
```

If you move `pipeline.py` to the project root, use `Path(__file__).resolve().parent` as `BASE_DIR` instead.

### `ModuleNotFoundError: No module named 'pandas'` or `streamlit`

Activate the intended virtual environment and run:

```powershell
python -m pip install -r ..\requirements.txt
```

Run this command from the `output/` folder if `requirements.txt` is in the project root.

### Dashboard says database not found

Run `python pipeline.py` first and confirm that `output/sales.db` has been generated.

### `no such table` error

The dashboard expects the pipeline to create `silver_sales`, `gold_product_sales`, and `gold_monthly_sales`. Run the pipeline again and confirm that it completed without an error.

### Kaggle CSV has different columns

Do not rename columns blindly. Inspect the file first, map the source columns to the target schema, and adapt validation rules to the meaning of the dataset. For example, a supermarket dataset may contain product categories but not individual product names.

## Limitations and Future Enhancements

This project is a learning prototype rather than a production data platform. Potential enhancements include:

1. **External data ingestion:** Import a Kaggle retail or supermarket dataset and document the source and schema mapping.
2. **Snowflake:** Replace or supplement SQLite with a cloud data warehouse.
3. **ETL/ELT design:** Separate extraction, transformation, and loading into reusable modules.
4. **Better duplicate handling:** Use a transaction-line identifier where orders can contain multiple items.
5. **Automated testing:** Add pytest tests for transformations and data-quality rules.
6. **Pipeline logging:** Record run timestamps, input counts, rejected counts, errors, and duration.
7. **Incremental loading:** Process only new or changed source records.
8. **Data governance:** Document data definitions, ownership, quality rules, and lineage.
9. **GenAI enrichment:** Prototype assisted product matching or standardization with human review.
10. **Deployment:** Publish the dashboard using a suitable hosting platform.

Only list enhancements as completed after you have implemented and tested them.

## Resume Description

After verifying that the relevant features work, you can describe the project like this:

**Sales Data Engineering Pipeline & Analytics Dashboard**  
*Python, pandas, SQL, SQLite, Streamlit*

- Built a sales data pipeline using Bronze, Silver, and Gold layers to ingest, validate, clean, and aggregate structured CSV data.
- Implemented data-quality checks for missing fields, invalid quantities/prices, and duplicate order IDs.
- Created SQL transformations to summarize monthly revenue and product performance.
- Developed a Streamlit dashboard for KPI monitoring, interactive filtering, and data-quality reporting.

Adjust these bullets to reflect the features you have actually implemented.

## Learning Outcomes

By completing this project, you can practice:

- CSV ingestion and schema validation.
- Data cleansing, standardization, and quality checks.
- Relational data storage and SQL aggregations.
- Medallion Architecture fundamentals.
- Interactive analytics using Streamlit.
- Reproducible setup, documentation, and Git-based project management.

These fundamentals are relevant to entry-level data engineering and Master Data Management roles, including roles that use Snowflake and cloud data platforms.

## License

Choose a license before publicly distributing the project. If you plan to reuse a third-party Kaggle dataset, review its dataset-specific license and usage terms. A license for your code does not automatically grant rights to redistribute the dataset.
