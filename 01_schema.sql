-- ============================================================
-- Computer Shop Sales — PostgreSQL Star Schema
-- Assumes standard computer-shop retail columns:
-- Invoice ID, Date, Customer Name, Customer Type, Product Name,
-- Category, Brand, Quantity, Unit Price, Total Price,
-- Payment Method, Salesperson, Branch/City
--
-- If your actual file uses different column names, adjust the CREATE TABLE
-- columns below AND the mapping dict in 02_load_data.py — that's the only
-- other place they appear.
-- ============================================================

DROP TABLE IF EXISTS fact_sales CASCADE;
DROP TABLE IF EXISTS dim_customer CASCADE;
DROP TABLE IF EXISTS dim_product CASCADE;
DROP TABLE IF EXISTS dim_employee CASCADE;
DROP TABLE IF EXISTS dim_branch CASCADE;
DROP TABLE IF EXISTS dim_date CASCADE;

-- ---------- Dimension: Date ----------
CREATE TABLE dim_date (
    date_key        DATE PRIMARY KEY,
    year            INT NOT NULL,
    quarter         INT NOT NULL,
    month           INT NOT NULL,
    month_name      VARCHAR(15) NOT NULL,
    day             INT NOT NULL,
    day_name        VARCHAR(15) NOT NULL,
    week_of_year    INT NOT NULL,
    is_weekend      BOOLEAN NOT NULL
);

-- ---------- Dimension: Customer ----------
CREATE TABLE dim_customer (
    customer_id     SERIAL PRIMARY KEY,
    customer_name   VARCHAR(150),
    customer_type   VARCHAR(50),   -- e.g. Retail / Wholesale / Corporate
    UNIQUE (customer_name, customer_type)
);

-- ---------- Dimension: Product ----------
CREATE TABLE dim_product (
    product_id      SERIAL PRIMARY KEY,
    product_name    VARCHAR(255),
    category        VARCHAR(100),   -- Laptop, Desktop, Monitor, Printer, Accessories, Networking
    brand           VARCHAR(100),
    UNIQUE (product_name, brand)
);

-- ---------- Dimension: Employee / Salesperson ----------
CREATE TABLE dim_employee (
    employee_id     SERIAL PRIMARY KEY,
    salesperson     VARCHAR(150) UNIQUE
);

-- ---------- Dimension: Branch ----------
CREATE TABLE dim_branch (
    branch_id       SERIAL PRIMARY KEY,
    branch_name     VARCHAR(150),
    city            VARCHAR(100),
    UNIQUE (branch_name, city)
);

-- ---------- Fact: Sales ----------
CREATE TABLE fact_sales (
    invoice_id      VARCHAR(30),
    sale_date       DATE NOT NULL REFERENCES dim_date(date_key),
    customer_id     INT REFERENCES dim_customer(customer_id),
    product_id      INT REFERENCES dim_product(product_id),
    employee_id     INT REFERENCES dim_employee(employee_id),
    branch_id       INT REFERENCES dim_branch(branch_id),
    quantity        INT NOT NULL,
    unit_price      NUMERIC(12,2) NOT NULL,
    total_price     NUMERIC(12,2) NOT NULL,
    payment_method  VARCHAR(30),
    PRIMARY KEY (invoice_id, product_id)
);

-- ---------- Indexes for DirectQuery performance ----------
CREATE INDEX idx_fact_sale_date  ON fact_sales(sale_date);
CREATE INDEX idx_fact_customer   ON fact_sales(customer_id);
CREATE INDEX idx_fact_product    ON fact_sales(product_id);
CREATE INDEX idx_fact_employee   ON fact_sales(employee_id);
CREATE INDEX idx_fact_branch     ON fact_sales(branch_id);

-- ---------- Read-only role for Power BI DirectQuery ----------
CREATE ROLE powerbi_reader LOGIN PASSWORD 'change_this_password';
GRANT CONNECT ON DATABASE computer_shop_db TO powerbi_reader;
GRANT USAGE ON SCHEMA public TO powerbi_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO powerbi_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO powerbi_reader;
