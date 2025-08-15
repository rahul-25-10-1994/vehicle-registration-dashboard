# Vehicle Registrations — Investor Dashboard (Streamlit)

A simple, investor-oriented dashboard for Vahan data. Upload maker-wise and vehicle-class-wise Excel exports for 2W/3W/4W. The app parses Indian-formatted numbers (e.g., `3,09,191`), aggregates by month/quarter/year, and computes **QoQ** and **YoY** growth by category and manufacturer.

## Quickstart

```bash
pip install -r requirements.txt
streamlit run app.py
```

In the sidebar, upload one or more Excel files (maker-wise and class-wise). If your file lacks a date/period column, set the **Year** input — the app will assign January 1st of that year as the period (good enough for **Yearly** or **Quarterly** views).

## Data Format

Works with tables similar to Vahan exports:
- **Maker-wise**: first column is manufacturer (e.g., *MARUTI SUZUKI INDIA LTD*), then columns like `4WIC, LMV, MMV, HMV, TOTAL`.
- **Vehicle-Class-wise**: first column is vehicle class (e.g., *MOTOR CAR*), same subcategory columns.

The app melts the subcategory columns into long format, adds `VehicleCategory` (2W/3W/4W inferred from file name or subcategory), and builds a unified time series.

## YoY & QoQ

After aggregating by Month/Quarter/Year, we compute:
- **QoQ%**: period-over-period growth
- **YoY%**: same month/quarter/year last year (12/4/1 periods)

## Optional SQL

We include **DuckDB** to run ad-hoc SQL (in-app example: quarterly totals). You can expand this in `utils.sql_example`.

## Scraping / Data Collection

If you wish to automate collection:
1. Manually visit the Vahan Dashboard and export the **Maker-wise** and **Vehicle-Class-wise** tables for each category (2W/3W/4W).
2. Save each as `YYYY_Category_Type.xlsx` so the app can infer the year (e.g., `2024_4W_maker.xlsx`, `2025_4W_vehicle_class.xlsx`).
3. For compliant automated retrieval, prefer **official APIs or scheduled manual downloads**. Avoid brittle HTML scraping; Vahan uses dynamic content. If you must automate, use a headless browser (Selenium) with human-like delays and proper attribution.

## Repository Structure

- `app.py` — Streamlit UI
- `utils.py` — data loaders, cleaning, aggregation, growth
- `requirements.txt` — deps
- `README.md` — this file

## Screen Recording

Record a 3–5 minute walkthrough:
- What the app does and how to upload files
- Show switching between **Quarterly** and **Yearly** views
- Filter by a few big manufacturers and comment on **YoY** winners
- Call out investor insights (e.g., 4W LMV momentum, EV-heavy makers gaining share)