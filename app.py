"""
Computer Shop Sales — End-to-End Streamlit Dashboard
Run locally:  streamlit run app.py
Deploy:       push to GitHub -> share.streamlit.io -> New app -> point to this repo/file
"""
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Computer Shop Sales Dashboard", layout="wide", page_icon="💻")

# ---------------------------------------------------------------
# 1. DATA LOADING
# ---------------------------------------------------------------
@st.cache_data
def load_data(path="computer shop.xlsx"):
    df = pd.read_excel(path)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.drop_duplicates().dropna(subset=["Date", "Total Price"])
    if "Total Price" not in df.columns or df["Total Price"].isnull().all():
        df["Total Price"] = df["Quantity"] * df["Unit Price"]
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.to_period("M").astype(str)
    return df

uploaded = st.sidebar.file_uploader("Upload computer shop.xlsx", type=["xlsx"])
df = load_data(uploaded) if uploaded else load_data()

# ---------------------------------------------------------------
# 2. SIDEBAR FILTERS
# ---------------------------------------------------------------
st.sidebar.header("Filters")

min_date, max_date = df["Date"].min(), df["Date"].max()
date_range = st.sidebar.date_input("Date Range", (min_date, max_date), min_value=min_date, max_value=max_date)

categories = st.sidebar.multiselect("Category", sorted(df["Category"].dropna().unique()), default=list(df["Category"].dropna().unique()))
brands = st.sidebar.multiselect("Brand", sorted(df["Brand"].dropna().unique()), default=list(df["Brand"].dropna().unique()))
branches = st.sidebar.multiselect("Branch", sorted(df["Branch"].dropna().unique()), default=list(df["Branch"].dropna().unique()))
payment_methods = st.sidebar.multiselect("Payment Method", sorted(df["Payment Method"].dropna().unique()), default=list(df["Payment Method"].dropna().unique()))

mask = (
    (df["Date"] >= pd.to_datetime(date_range[0]))
    & (df["Date"] <= pd.to_datetime(date_range[1]))
    & (df["Category"].isin(categories))
    & (df["Brand"].isin(brands))
    & (df["Branch"].isin(branches))
    & (df["Payment Method"].isin(payment_methods))
)
fdf = df[mask]

# ---------------------------------------------------------------
# 3. KPI CARDS
# ---------------------------------------------------------------
st.title("💻 Computer Shop Sales — End-to-End Dashboard")

total_revenue = fdf["Total Price"].sum()
total_units = fdf["Quantity"].sum()
invoice_count = fdf["Invoice ID"].nunique()
avg_sale = total_revenue / invoice_count if invoice_count else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Revenue", f"${total_revenue:,.0f}")
c2.metric("Units Sold", f"{total_units:,}")
c3.metric("Invoices", f"{invoice_count:,}")
c4.metric("Avg Sale Value", f"${avg_sale:,.2f}")

st.divider()

# ---------------------------------------------------------------
# 4. TREND CHART
# ---------------------------------------------------------------
trend = fdf.groupby("Month")["Total Price"].sum().reset_index()
fig_trend = px.line(trend, x="Month", y="Total Price", markers=True, title="Monthly Revenue Trend")
st.plotly_chart(fig_trend, use_container_width=True)

# ---------------------------------------------------------------
# 5. CATEGORY / BRAND BREAKDOWN
# ---------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    cat = fdf.groupby("Category")["Total Price"].sum().reset_index()
    fig_cat = px.bar(cat, x="Category", y="Total Price", title="Revenue by Category")
    st.plotly_chart(fig_cat, use_container_width=True)

with col2:
    brand = fdf.groupby("Brand")["Total Price"].sum().reset_index()
    fig_brand = px.pie(brand, names="Brand", values="Total Price", title="Revenue Share by Brand", hole=0.4)
    st.plotly_chart(fig_brand, use_container_width=True)

# ---------------------------------------------------------------
# 6. PAYMENT METHOD & BRANCH PERFORMANCE
# ---------------------------------------------------------------
col3, col4 = st.columns(2)

with col3:
    pay = fdf.groupby("Payment Method")["Total Price"].sum().reset_index()
    fig_pay = px.bar(pay, x="Payment Method", y="Total Price", title="Revenue by Payment Method")
    st.plotly_chart(fig_pay, use_container_width=True)

with col4:
    branch = fdf.groupby("Branch")["Total Price"].sum().sort_values(ascending=False).reset_index()
    fig_branch = px.bar(branch, x="Branch", y="Total Price", title="Revenue by Branch")
    st.plotly_chart(fig_branch, use_container_width=True)

# ---------------------------------------------------------------
# 7. TOP SALESPEOPLE TABLE + DRILL-DOWN
# ---------------------------------------------------------------
st.subheader("Top 10 Salespeople")
top_sales = (fdf.groupby("Salesperson")["Total Price"].sum()
               .sort_values(ascending=False).head(10).reset_index()
               .rename(columns={"Total Price": "Revenue"}))
st.dataframe(top_sales, use_container_width=True)

with st.expander("🔍 View filtered raw data"):
    st.dataframe(fdf, use_container_width=True)
    st.download_button("Download filtered data (CSV)", fdf.to_csv(index=False), "filtered_sales.csv")

st.caption("Built with Streamlit · pandas · Plotly — data updates automatically as filters change.")
