"""
Loads computer shop.xlsx into the PostgreSQL star schema defined in 01_schema.sql.

pip install pandas sqlalchemy psycopg2-binary openpyxl --break-system-packages

Usage:
    python 02_load_data.py
"""
import pandas as pd
from sqlalchemy import create_engine

# ---------- 1. CONFIG — edit these two things only ----------
EXCEL_PATH = "computer shop.xlsx"

# If your real column headers differ, map them here: "your_header": "standard_name"
COLUMN_MAP = {
    "Invoice ID": "invoice_id",
    "Date": "sale_date",
    "Customer Name": "customer_name",
    "Customer Type": "customer_type",
    "Product Name": "product_name",
    "Category": "category",
    "Brand": "brand",
    "Quantity": "quantity",
    "Unit Price": "unit_price",
    "Total Price": "total_price",
    "Payment Method": "payment_method",
    "Salesperson": "salesperson",
    "Branch": "branch_name",
    "City": "city",
}

DB_URI = "postgresql+psycopg2://postgres:your_password@localhost:5432/computer_shop_db"

# ---------- 2. Load & clean ----------
df = pd.read_excel(EXCEL_PATH)
df = df.rename(columns=COLUMN_MAP)
df["sale_date"] = pd.to_datetime(df["sale_date"]).dt.date
df = df.drop_duplicates()
df = df.dropna(subset=["invoice_id", "sale_date", "total_price"])

# derive total_price if the sheet only has quantity * unit_price
if "total_price" not in df.columns or df["total_price"].isnull().all():
    df["total_price"] = df["quantity"] * df["unit_price"]

engine = create_engine(DB_URI)

# ---------- 3. dim_date ----------
dim_date = pd.DataFrame({"date_key": pd.to_datetime(df["sale_date"].unique())})
dim_date["year"] = dim_date.date_key.dt.year
dim_date["quarter"] = dim_date.date_key.dt.quarter
dim_date["month"] = dim_date.date_key.dt.month
dim_date["month_name"] = dim_date.date_key.dt.month_name()
dim_date["day"] = dim_date.date_key.dt.day
dim_date["day_name"] = dim_date.date_key.dt.day_name()
dim_date["week_of_year"] = dim_date.date_key.dt.isocalendar().week
dim_date["is_weekend"] = dim_date.date_key.dt.dayofweek >= 5
dim_date.to_sql("dim_date", engine, if_exists="append", index=False)

# ---------- 4. dim_customer ----------
dim_customer = df[["customer_name", "customer_type"]].drop_duplicates()
dim_customer.to_sql("dim_customer", engine, if_exists="append", index=False)
dim_customer_db = pd.read_sql("SELECT * FROM dim_customer", engine)

# ---------- 5. dim_product ----------
dim_product = df[["product_name", "category", "brand"]].drop_duplicates()
dim_product.to_sql("dim_product", engine, if_exists="append", index=False)
dim_product_db = pd.read_sql("SELECT * FROM dim_product", engine)

# ---------- 6. dim_employee ----------
dim_employee = df[["salesperson"]].drop_duplicates()
dim_employee.to_sql("dim_employee", engine, if_exists="append", index=False)
dim_employee_db = pd.read_sql("SELECT * FROM dim_employee", engine)

# ---------- 7. dim_branch ----------
dim_branch = df[["branch_name", "city"]].drop_duplicates()
dim_branch.to_sql("dim_branch", engine, if_exists="append", index=False)
dim_branch_db = pd.read_sql("SELECT * FROM dim_branch", engine)

# ---------- 8. Merge back surrogate keys for fact table ----------
fact = (
    df.merge(dim_customer_db, on=["customer_name", "customer_type"], how="left")
      .merge(dim_product_db, on=["product_name", "category", "brand"], how="left")
      .merge(dim_employee_db, on=["salesperson"], how="left")
      .merge(dim_branch_db, on=["branch_name", "city"], how="left")
)

fact_cols = ["invoice_id", "sale_date", "customer_id", "product_id", "employee_id",
             "branch_id", "quantity", "unit_price", "total_price", "payment_method"]
fact[fact_cols].to_sql("fact_sales", engine, if_exists="append", index=False)

print(f"Loaded {len(fact)} rows into fact_sales.")
