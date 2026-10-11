
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

# --------------------------------------------------
# 1. CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
DB_FILE = OUTPUT_DIR / "sales.db"
REJECTED_FILE = OUTPUT_DIR / "rejected_sales.csv"

st.set_page_config(
    page_title="Sales Intelligence | Data Pipeline",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# 2. CUSTOM STYLING
# --------------------------------------------------

st.markdown("""
<style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    div[data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.20);
        padding: 16px;
        border-radius: 12px;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 14px;
    }

    .section-note {
        color: #808080;
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 3. LOAD DATABASE
# --------------------------------------------------

st.sidebar.title("📊 Sales Intelligence")
st.sidebar.caption("Data Engineering Analytics")
st.sidebar.divider()

if not DB_FILE.exists():
    st.error(
        "Database not found. Please run "
        "`python pipeline.py` from your output folder."
    )
    st.stop()

try:
    with sqlite3.connect(DB_FILE) as conn:
        sales = pd.read_sql_query(
            "SELECT * FROM silver_sales",
            conn
        )

        products_gold = pd.read_sql_query(
            "SELECT * FROM gold_product_sales",
            conn
        )

        monthly_gold = pd.read_sql_query(
            "SELECT * FROM gold_monthly_sales",
            conn
        )

except Exception as error:
    st.error(f"Unable to load the database: {error}")
    st.stop()

if sales.empty:
    st.warning("No valid sales records are available.")
    st.stop()

# --------------------------------------------------
# 4. PREPARE DATA
# --------------------------------------------------

sales["order_date"] = pd.to_datetime(
    sales["order_date"], errors="coerce"
)

sales["quantity"] = pd.to_numeric(
    sales["quantity"], errors="coerce"
)

sales["unit_price"] = pd.to_numeric(
    sales["unit_price"], errors="coerce"
)

sales["revenue"] = pd.to_numeric(
    sales["revenue"], errors="coerce"
)

sales["category"] = sales["category"].fillna("Unknown")
sales["product"] = sales["product"].fillna("Unknown")

# --------------------------------------------------
# 5. SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.subheader("Filters")

valid_dates = sales["order_date"].dropna()

if valid_dates.empty:
    st.error("No valid order dates are available.")
    st.stop()

min_date = valid_dates.min().date()
max_date = valid_dates.max().date()

date_range = st.sidebar.date_input(
    "Order date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

categories = sorted(sales["category"].unique().tolist())

selected_categories = st.sidebar.multiselect(
    "Product category",
    options=categories,
    default=categories
)

available_products = sorted(
    sales[
        sales["category"].isin(selected_categories)
    ]["product"].unique().tolist()
)

selected_products = st.sidebar.multiselect(
    "Product",
    options=available_products,
    default=available_products
)

# Apply filters
filtered = sales.copy()

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range

    filtered = filtered[
        filtered["order_date"].dt.date.between(
            start_date, end_date
        )
    ]

filtered = filtered[
    filtered["category"].isin(selected_categories)
    & filtered["product"].isin(selected_products)
]

st.sidebar.divider()
st.sidebar.caption(f"Showing {len(filtered)} of {len(sales)} valid records.")

# --------------------------------------------------
# 6. HEADER
# --------------------------------------------------

st.title("📊 Sales Intelligence Dashboard")

st.markdown(
    "Monitor sales performance, explore product trends, "
    "and review data quality across your data pipeline."
)

st.caption(
    "Architecture: Bronze → Silver → Gold | "
    "Powered by Python, pandas, SQL and SQLite"
)

st.divider()

# --------------------------------------------------
# 7. KPI CARDS
# --------------------------------------------------

total_revenue = filtered["revenue"].sum()
total_orders = filtered["order_id"].nunique()
units_sold = filtered["quantity"].sum()

average_order_value = (
    total_revenue / total_orders
    if total_orders else 0
)

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Total Revenue",
    f"₹{total_revenue:,.2f}"
)

k2.metric(
    "Total Orders",
    f"{total_orders:,}"
)

k3.metric(
    "Units Sold",
    f"{units_sold:,.0f}"
)

k4.metric(
    "Average Order Value",
    f"₹{average_order_value:,.2f}"
)

st.markdown("")

# --------------------------------------------------
# 8. CHARTS
# --------------------------------------------------

st.subheader("Sales Performance")

if filtered.empty:
    st.info("No sales match the selected filters.")
else:
    chart_left, chart_right = st.columns(2)

    with chart_left:
        st.markdown("**Monthly Revenue Trend**")

        monthly = (
            filtered.assign(
                month=filtered["order_date"].dt.to_period("M").astype(str)
            )
            .groupby("month", as_index=False)["revenue"]
            .sum()
            .sort_values("month")
            .set_index("month")
        )

        st.line_chart(
            monthly,
            y="revenue",
            x_label="Month",
            y_label="Revenue (₹)",
            use_container_width=True
        )

    with chart_right:
        st.markdown("**Revenue by Product**")

        product_chart = (
            filtered.groupby("product", as_index=False)["revenue"]
            .sum()
            .sort_values("revenue", ascending=False)
            .set_index("product")
        )

        st.bar_chart(
            product_chart,
            y="revenue",
            x_label="Product",
            y_label="Revenue (₹)",
            use_container_width=True
        )

    st.markdown("**Revenue by Category**")

    category_chart = (
        filtered.groupby("category", as_index=False)["revenue"]
        .sum()
        .sort_values("revenue", ascending=False)
        .set_index("category")
    )

    st.bar_chart(
        category_chart,
        y="revenue",
        x_label="Category",
        y_label="Revenue (₹)",
        use_container_width=True
    )

# --------------------------------------------------
# 9. PRODUCT ANALYSIS
# --------------------------------------------------

st.divider()
st.subheader("🏆 Product Performance")

if filtered.empty:
    st.info("No product data for the selected filters.")
else:
    product_summary = (
        filtered.groupby(["product", "category"], as_index=False)
        .agg(
            units_sold=("quantity", "sum"),
            total_orders=("order_id", "nunique"),
            total_revenue=("revenue", "sum")
        )
    )

    product_summary["total_revenue"] = (
        product_summary["total_revenue"].round(2)
    )

    product_summary = product_summary.sort_values(
        "total_revenue", ascending=False
    )

    st.dataframe(
        product_summary,
        use_container_width=True,
        hide_index=True
    )

# --------------------------------------------------
# 10. SALES DATA EXPLORER
# --------------------------------------------------

st.divider()
st.subheader("🔎 Sales Data Explorer")

if filtered.empty:
    st.info("No records available to display.")
else:
    display_columns = [
        "order_id",
        "order_date",
        "customer_id",
        "product",
        "category",
        "quantity",
        "unit_price",
        "revenue"
    ]

    explorer = filtered[display_columns].copy()

    explorer["order_date"] = (
        explorer["order_date"].dt.strftime("%Y-%m-%d")
    )

    st.dataframe(
        explorer.sort_values(
            "order_date", ascending=False
        ),
        use_container_width=True,
        hide_index=True
    )

    csv_data = explorer.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️ Download Filtered Sales CSV",
        data=csv_data,
        file_name="filtered_sales.csv",
        mime="text/csv"
    )

# --------------------------------------------------
# 11. DATA QUALITY MONITOR
# --------------------------------------------------

st.divider()
st.subheader("🛡️ Data Quality Monitor")

if REJECTED_FILE.exists():
    rejected = pd.read_csv(REJECTED_FILE)

    total_source_records = len(sales) + len(rejected)
    rejected_count = len(rejected)

    # Duplicate records removed by the pipeline are
    # not present in silver_sales or rejected_sales.csv.
    duplicate_count = max(
        total_source_records
        - rejected_count
        - sales["order_id"].nunique(),
        0
    )

    quality_rate = (
        len(sales) / total_source_records * 100
        if total_source_records else 0
    )

    q1, q2, q3 = st.columns(3)

    q1.metric(
        "Valid Records",
        f"{len(sales):,}"
    )

    q2.metric(
        "Rejected Records",
        f"{rejected_count:,}"
    )

    q3.metric(
        "Valid Record Rate",
        f"{quality_rate:.1f}%"
    )

    st.progress(quality_rate / 100)

    if not rejected.empty:
        st.markdown("**Rejected Records for Investigation**")
        st.dataframe(
            rejected,
            use_container_width=True,
            hide_index=True
        )

    with st.expander("About data quality metrics"):
        st.write(
            "Valid Record Rate = valid Silver records divided "
            "by (valid Silver records + rejected records). "
            "Duplicate order IDs removed during processing are "
            "not included in this denominator."
        )

        st.write(
            f"Duplicate order IDs removed (estimated): "
            f"{duplicate_count}"
        )

else:
    st.info(
        "Quality report not found. Run pipeline.py to generate it."
    )

# --------------------------------------------------
# 12. FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Sales Intelligence | Python • pandas • SQL • SQLite • Streamlit"
)
