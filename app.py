import streamlit as st
import pandas as pd
import plotly.express as px
import os

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title='Computer Shop Sales Dashboard',
    page_icon='💻',
    layout='wide'
)

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data(uploaded_file=None):

    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
    else:
        file_path = 'computer shop.xlsx'

        if not os.path.exists(file_path):
            return None

        df = pd.read_excel(file_path)

    # Rename columns
    df = df.rename(columns={
        'Order Date': 'Date',
        'Order id': 'Order_ID',
        'Cust Name': 'Customer',
        'Product': 'Product_Name',
        'Qty': 'Quantity',
        'Amount': 'Total_Sales',
        'Profit 10%': 'Profit'
    })

    # Date conversion
    df['Date'] = pd.to_datetime(df['Date'])

    # Time columns
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.strftime('%Y-%m')

    return df


# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title('📂 Data Upload')

uploaded_file = st.sidebar.file_uploader(
    'Upload Excel File',
    type=['xlsx']
)

df = load_data(uploaded_file)

if df is None:
    st.warning('Please upload computer shop.xlsx file')
    st.stop()

# -----------------------------
# FILTERS
# -----------------------------
st.sidebar.title('🔎 Filters')

region_filter = st.sidebar.multiselect(
    'Select Region',
    options=df['Region'].unique(),
    default=df['Region'].unique()
)

category_filter = st.sidebar.multiselect(
    'Select Category',
    options=df['Category'].unique(),
    default=df['Category'].unique()
)

filtered_df = df[
    (df['Region'].isin(region_filter)) &
    (df['Category'].isin(category_filter))
]

# -----------------------------
# KPI CARDS
# -----------------------------
st.title('💻 Computer Shop Sales Dashboard')

total_sales = filtered_df['Total_Sales'].sum()
total_profit = filtered_df['Profit'].sum()
total_orders = filtered_df['Order_ID'].nunique()
total_customers = filtered_df['Customer'].nunique()

col1, col2, col3, col4 = st.columns(4)

col1.metric('Total Sales', f'${total_sales:,.0f}')
col2.metric('Total Profit', f'${total_profit:,.0f}')
col3.metric('Total Orders', f'{total_orders:,}')
col4.metric('Total Customers', f'{total_customers:,}')

st.divider()

# -----------------------------
# MONTHLY SALES TREND
# -----------------------------
monthly_sales = filtered_df.groupby('Month')['Total_Sales'].sum().reset_index()

fig1 = px.line(
    monthly_sales,
    x='Month',
    y='Total_Sales',
    markers=True,
    title='📈 Monthly Sales Trend'
)

st.plotly_chart(fig1, use_container_width=True)

# -----------------------------
# CATEGORY ANALYSIS
# -----------------------------
col5, col6 = st.columns(2)

with col5:
    category_sales = filtered_df.groupby('Category')['Total_Sales'].sum().reset_index()

    fig2 = px.bar(
        category_sales,
        x='Category',
        y='Total_Sales',
        title='📦 Sales by Category',
        text_auto=True
    )

    st.plotly_chart(fig2, use_container_width=True)

with col6:
    region_sales = filtered_df.groupby('Region')['Total_Sales'].sum().reset_index()

    fig3 = px.pie(
        region_sales,
        names='Region',
        values='Total_Sales',
        title='🌍 Sales by Region',
        hole=0.4
    )

    st.plotly_chart(fig3, use_container_width=True)

# -----------------------------
# TOP PRODUCTS
# -----------------------------
st.subheader('🏆 Top 10 Products')

top_products = (
    filtered_df.groupby('Product_Name')['Total_Sales']
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig4 = px.bar(
    top_products,
    x='Total_Sales',
    y='Product_Name',
    orientation='h',
    title='Top Products by Revenue',
    text_auto=True
)

st.plotly_chart(fig4, use_container_width=True)

# -----------------------------
# TOP CUSTOMERS
# -----------------------------
st.subheader('👥 Top 10 Customers')

top_customers = (
    filtered_df.groupby('Customer')['Total_Sales']
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

st.dataframe(top_customers, use_container_width=True)

# -----------------------------
# RAW DATA
# -----------------------------
with st.expander('📋 View Raw Data'):
    st.dataframe(filtered_df, use_container_width=True)

    csv = filtered_df.to_csv(index=False)

    st.download_button(
        label='⬇ Download Filtered Data',
        data=csv,
        file_name='filtered_sales.csv',
        mime='text/csv'
    )

st.caption('Built with Streamlit • Pandas • Plotly')