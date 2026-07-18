# Computer Shop Sales — Full Project (DSA7 Final Project)

Dataset: `computer shop.xlsx` (from the course dataset repo)

## Folder guide
```
sql/
  01_schema.sql        -> PostgreSQL star schema (run this first, in psql or pgAdmin)
  02_load_data.py       -> loads the Excel file into the Postgres tables
powerbi/
  DAX_Measures_and_Setup.md  -> DirectQuery connection steps + all DAX measures
eda/
  EDA_ComputerShop_Analysis.ipynb  -> full Jupyter EDA (pandas/matplotlib/seaborn)
streamlit_app/
  app.py, requirements.txt  -> end-to-end interactive dashboard
```

## ⚠️ Column-name assumption
GitHub blocks direct download of the raw `.xlsx` binary in this environment, so this
project assumes the standard computer-shop retail column set: `Invoice ID, Date,
Customer Name, Customer Type, Product Name, Category, Brand, Quantity, Unit Price,
Total Price, Payment Method, Salesperson, Branch, City`. **Open your actual downloaded
file first** — if any header differs, update it in exactly two places: `COLUMN_MAP` in
`sql/02_load_data.py`, and the matching column references in `streamlit_app/app.py`
and the notebook's load cell.

## Task 1 — PostgreSQL + Power BI (DirectQuery)
1. Install PostgreSQL locally (or use a free cloud instance — Supabase/Neon).
2. `createdb computer_shop_db`
3. Run `psql -d computer_shop_db -f sql/01_schema.sql`
4. Edit `DB_URI` and `EXCEL_PATH` at the top of `sql/02_load_data.py`, then:
   `pip install pandas sqlalchemy psycopg2-binary openpyxl --break-system-packages`
   `python sql/02_load_data.py`
5. Follow `powerbi/DAX_Measures_and_Setup.md` to connect Power BI in **DirectQuery**
   mode and build the 5 dashboard pages with the provided DAX measures.

## Task 2a — Jupyter EDA
1. `pip install pandas numpy matplotlib seaborn openpyxl jupyter --break-system-packages`
2. Place `computer shop.xlsx` in the same folder as the notebook.
3. `jupyter notebook eda/EDA_ComputerShop_Analysis.ipynb` and run all cells.
4. Fill in the markdown "Insight cells" with your actual observed numbers.

## Task 2b — Streamlit Dashboard + Live Deployment
**Local run:**
```
cd streamlit_app
pip install -r requirements.txt --break-system-packages
streamlit run app.py
```

**Deploy to Streamlit Community Cloud (free):**
1. Push `streamlit_app/` (including the Excel file, or rely on the in-app uploader)
   to a public GitHub repo.
2. Go to https://share.streamlit.io → Sign in with GitHub → New app.
3. Select the repo, branch, and set the file path to `app.py`.
4. Click Deploy — you get a public `*.streamlit.app` URL to submit.

## Suggested submission order
1. Screenshot/export Power BI dashboard pages + a short note proving DirectQuery
   (edit a row in Postgres, refresh Power BI, show it updates).
2. Export the Jupyter notebook as PDF/HTML for the written EDA report.
3. Submit the live Streamlit URL + GitHub repo link.
