
import sqlite3
from pathlib import Path

import pandas as pd

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "sales.csv"
OUTPUT_DIR = BASE_DIR / "output"
DB_FILE = OUTPUT_DIR / "sales.db"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 1. Extract raw sales data
if not DATA_FILE.exists():
    raise FileNotFoundError(
        f"Sales CSV not found: {DATA_FILE}\n"
        "Make sure sales.csv exists inside the data folder."
    )

raw = pd.read_csv(
    DATA_FILE,
    dtype=str,
    keep_default_na=False
)

print(f"Source records: {len(raw)}")

# Check required columns
required_columns = [
    "order_id", "order_date", "product", "category",
    "quantity", "unit_price", "customer_id"
]

missing_columns = set(required_columns) - set(raw.columns)

if missing_columns:
    raise ValueError(f"Missing CSV columns: {sorted(missing_columns)}")

# 2. Bronze layer: preserve original source records
with sqlite3.connect(DB_FILE) as conn:
    raw.to_sql(
        "bronze_sales",
        conn,
        if_exists="replace",
        index=False
    )

# 3. Silver layer: clean and validate
clean = raw.copy()

for column in [
    "order_id", "product", "category", "customer_id"
]:
    clean[column] = clean[column].str.strip()

clean["order_date"] = pd.to_datetime(
    clean["order_date"],
    errors="coerce"
)

clean["quantity"] = pd.to_numeric(
    clean["quantity"],
    errors="coerce"
)

clean["unit_price"] = pd.to_numeric(
    clean["unit_price"],
    errors="coerce"
)

# Required field validation
valid = clean[required_columns].notna().all(axis=1)

for column in ["order_id", "product", "category", "customer_id"]:
    valid &= clean[column].ne("")

valid &= clean["quantity"].gt(0)
valid &= clean["unit_price"].ge(0)

# Store invalid rows for investigation
rejected = clean.loc[~valid].copy()

rejected.to_csv(
    OUTPUT_DIR / "rejected_sales.csv",
    index=False
)

# Keep valid records
clean = clean.loc[valid].copy()

# Remove duplicate order IDs
before_dedup = len(clean)

clean = clean.drop_duplicates(
    subset=["order_id"],
    keep="first"
)

duplicates_removed = before_dedup - len(clean)

# Standardize dates and calculate revenue
clean["order_date"] = clean["order_date"].dt.strftime("%Y-%m-%d")
clean["quantity"] = clean["quantity"].astype(int)
clean["unit_price"] = clean["unit_price"].astype(float)

clean["revenue"] = (
    clean["quantity"] * clean["unit_price"]
).round(2)

# 4. Load Silver and create Gold tables
with sqlite3.connect(DB_FILE) as conn:
    clean.to_sql(
        "silver_sales",
        conn,
        if_exists="replace",
        index=False
    )

    # Recreate Gold tables on every run
    conn.execute("DROP TABLE IF EXISTS gold_product_sales")
    conn.execute("DROP TABLE IF EXISTS gold_monthly_sales")

    # Gold: product performance
    conn.execute("""
        CREATE TABLE gold_product_sales AS
        SELECT
            product,
            category,
            SUM(quantity) AS units_sold,
            ROUND(SUM(revenue), 2) AS total_revenue
        FROM silver_sales
        GROUP BY product, category
    """)

    # Gold: monthly sales
    conn.execute("""
        CREATE TABLE gold_monthly_sales AS
        SELECT
            substr(order_date, 1, 7) AS sales_month,
            COUNT(DISTINCT order_id) AS total_orders,
            ROUND(SUM(revenue), 2) AS total_revenue
        FROM silver_sales
        GROUP BY substr(order_date, 1, 7)
    """)

    silver_count = conn.execute(
        "SELECT COUNT(*) FROM silver_sales"
    ).fetchone()[0]

    total_revenue = conn.execute(
        "SELECT COALESCE(ROUND(SUM(revenue), 2), 0) "
        "FROM silver_sales"
    ).fetchone()[0]

    product_count = conn.execute(
        "SELECT COUNT(*) FROM gold_product_sales"
    ).fetchone()[0]

# 5. Pipeline report
print("\n========== PIPELINE REPORT ==========")
print(f"Source records       : {len(raw)}")
print(f"Rejected records     : {len(rejected)}")
print(f"Duplicates removed   : {duplicates_removed}")
print(f"Silver records       : {silver_count}")
print(f"Products summarized  : {product_count}")
print(f"Total revenue        : {total_revenue:,.2f}")
print(f"Database location    : {DB_FILE}")
print("Pipeline completed successfully!")
