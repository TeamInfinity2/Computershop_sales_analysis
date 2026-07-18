# Power BI — DirectQuery Setup + DAX Measures (Computer Shop)

## 1. Connect Power BI to PostgreSQL (DirectQuery)

1. Install the **Npgsql** driver: https://www.npgsql.org/ → download the latest `.msi`.
2. Power BI Desktop → **Home → Get Data → More → Database → PostgreSQL database**.
3. Server: `localhost:5432` · Database: `computer_shop_db`
4. **Data Connectivity mode: DirectQuery** (not Import — this is what makes it "live").
5. Credentials: use the `powerbi_reader` role from `01_schema.sql`.
6. Load `fact_sales`, `dim_date`, `dim_customer`, `dim_product`, `dim_employee`, `dim_branch`.
7. In **Model view**, confirm relationships (should auto-detect via FK names):
   - `fact_sales[sale_date]` → `dim_date[date_key]`
   - `fact_sales[customer_id]` → `dim_customer[customer_id]`
   - `fact_sales[product_id]` → `dim_product[product_id]`
   - `fact_sales[employee_id]` → `dim_employee[employee_id]`
   - `fact_sales[branch_id]` → `dim_branch[branch_id]`
8. Mark `dim_date` as a **Date Table**: select table → Table tools → Mark as date table → `date_key`.

Verify DirectQuery is live: edit a row's `total_price` directly in Postgres, hit Refresh in Power BI — the visual should update without a full re-import.

## 2. DAX Measures

Create these in a dedicated **Measures** table.

### Core measures
```dax
Total Revenue = SUM(fact_sales[total_price])

Total Units Sold = SUM(fact_sales[quantity])

Invoice Count = DISTINCTCOUNT(fact_sales[invoice_id])

Avg Sale Value = DIVIDE([Total Revenue], [Invoice Count])

Avg Unit Price = AVERAGE(fact_sales[unit_price])
```

### Time intelligence (requires dim_date marked as date table)
```dax
Revenue LY = CALCULATE([Total Revenue], SAMEPERIODLASTYEAR(dim_date[date_key]))

Revenue YoY % = DIVIDE([Total Revenue] - [Revenue LY], [Revenue LY])

Revenue MTD = TOTALMTD([Total Revenue], dim_date[date_key])

Revenue QTD = TOTALQTD([Total Revenue], dim_date[date_key])

Revenue YTD = TOTALYTD([Total Revenue], dim_date[date_key])

Rolling 3M Revenue =
CALCULATE(
    [Total Revenue],
    DATESINPERIOD(dim_date[date_key], MAX(dim_date[date_key]), -3, MONTH)
)
```

### Ranking & contribution
```dax
Revenue Rank (Product) =
RANKX(ALL(dim_product[product_name]), [Total Revenue], , DESC)

% of Total Revenue =
DIVIDE([Total Revenue], CALCULATE([Total Revenue], ALL(fact_sales)))

Top Salesperson Revenue =
CALCULATE([Total Revenue], TOPN(1, ALL(dim_employee[salesperson]), [Total Revenue]))
```

### Category / Brand diagnostics
```dax
Revenue by Category Share =
DIVIDE([Total Revenue], CALCULATE([Total Revenue], ALLEXCEPT(dim_product, dim_product[category])))

Avg Basket Size (Units) = DIVIDE([Total Units Sold], [Invoice Count])

Repeat Customer Flag =
CALCULATE(DISTINCTCOUNT(fact_sales[invoice_id]), ALLEXCEPT(dim_customer, dim_customer[customer_id])) > 1
```

### Payment method / branch performance
```dax
Cash Sales % =
DIVIDE(CALCULATE([Total Revenue], fact_sales[payment_method] = "Cash"), [Total Revenue])

Branch Revenue Rank =
RANKX(ALL(dim_branch[branch_name]), [Total Revenue], , DESC)
```

## 3. Suggested dashboard pages
1. **Executive Summary** — Total Revenue, Units Sold, Invoice Count, Avg Sale Value cards; monthly revenue trend; YoY % KPI.
2. **Product Performance** — Category/Brand bar chart with Revenue Rank; top 10 products table.
3. **Sales Team & Branch** — Salesperson leaderboard; Branch Revenue Rank map/table.
4. **Customer & Payment** — Customer type split; payment method donut; repeat-customer rate.
5. **Trend & Forecast** — Revenue MTD/QTD/YTD cards, rolling 3-month line.

Add a **slicer panel** (date range, category, brand, branch, payment method) synced across pages via Edit Interactions.
