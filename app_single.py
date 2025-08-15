import streamlit as st
import pandas as pd
import plotly.express as px
import re
from pathlib import Path
import os


# -----------------------
# Helper Functions
# -----------------------
def clean_columns(df):
    """Strip and normalize column names."""
    df.columns = [str(c).strip() for c in df.columns]
    return df


def to_int(val):
    """Convert value with commas/NaN to int if possible."""
    try:
        if pd.isna(val):
            return 0
        val = str(val).replace(",", "").strip()
        return int(float(val))
    except Exception:
        return 0


def load_vahan_file(file, year: int | None = None, sheet_name=0) -> pd.DataFrame:
    """Load Maker-wise or Vehicle-Class-wise Excel/CSV and reshape to long format."""
    ext = os.path.splitext(file.name)[1].lower()

    if ext in [".xlsx", ".xls", ".xlsb"]:
        df = pd.read_excel(file, sheet_name=sheet_name, header=0, engine="openpyxl")
    elif ext == ".csv":
        df = pd.read_csv(file)
    else:
        st.error(f"Unsupported file type: {ext}")
        return None

    df = clean_columns(df)
    df = df.dropna(axis=1, how="all")

    # Guess entity column
    entity_col = None
    for c in df.columns:
        c_norm = c.lower()
        if any(k in c_norm for k in ["maker", "manufacturer", "vehicle class", "vehicle"]):
            entity_col = c
            break
    if entity_col is None:
        entity_col = df.columns[0]

    drop_like = {"S No", "S. No", "SNo", "SNo."}
    metric_cols = [c for c in df.columns if c not in drop_like | {entity_col}]

    for c in metric_cols:
        df[c] = df[c].apply(to_int)

    long_df = df.melt(id_vars=[entity_col], value_vars=metric_cols,
                      var_name="Subcategory", value_name="Registrations")

    if "Year" not in long_df.columns:
        if year is None:
            try:
                name = Path(getattr(file, "name", "data")).name
                year_guess = [int(s) for s in re.findall(r"(20\d{2})", name)]
                year = year_guess[0] if year_guess else None
            except Exception:
                year = None
        long_df["Year"] = year

    if "Period" not in long_df.columns:
        if long_df["Year"].notna().any():
            long_df["Period"] = pd.to_datetime(long_df["Year"].fillna(1970).astype(int).astype(str) + "-01-01")
        else:
            long_df["Period"] = pd.Timestamp.today().normalize()

    name = Path(getattr(file, "name", "")).name.lower()
    if any(k in name for k in ["two", "2w"]):
        vehicle_category = "2W"
    elif any(k in name for k in ["three", "3w"]):
        vehicle_category = "3W"
    elif any(k in name for k in ["four", "4w"]):
        vehicle_category = "4W"
    else:
        if long_df["Subcategory"].str.contains("4W", case=False, na=False).any():
            vehicle_category = "4W"
        elif long_df["Subcategory"].str.contains("3W", case=False, na=False).any():
            vehicle_category = "3W"
        elif long_df["Subcategory"].str.contains("2W", case=False, na=False).any():
            vehicle_category = "2W"
        else:
            vehicle_category = "Unknown"

    long_df["VehicleCategory"] = vehicle_category
    long_df = long_df.rename(columns={entity_col: "Entity"})
    long_df["Registrations"] = long_df["Registrations"].astype(int)
    long_df["Period"] = pd.to_datetime(long_df["Period"])
    return long_df


def plot_registrations(df, title="Registrations over Time"):
    fig = px.line(df, x="Period", y="Registrations", color="Entity", markers=True, title=title)
    st.plotly_chart(fig, use_container_width=True)


# -----------------------
# Streamlit App
# -----------------------
st.set_page_config(page_title="Vehicle Registration Dashboard", layout="wide")

st.title("📊 Vehicle Registration Dashboard (Excel & CSV)")

maker_files = st.file_uploader(
    "Upload Maker-wise files (Excel/CSV)", 
    type=["xlsx", "xls", "xlsb", "csv"], 
    accept_multiple_files=True
)

class_files = st.file_uploader(
    "Upload Vehicle-Class-wise files (Excel/CSV, optional)", 
    type=["xlsx", "xls", "xlsb", "csv"], 
    accept_multiple_files=True
)

if maker_files:
    dfs = []
    for f in maker_files:
        df = load_vahan_file(f)
        if df is not None:
            dfs.append(df)

    if dfs:
        combined_df = pd.concat(dfs, ignore_index=True)
        st.subheader("Raw Combined Data")
        st.dataframe(combined_df.head(20))

        st.subheader("Registrations Trend")
        plot_registrations(combined_df)

        st.subheader("Top Entities")
        top_df = (combined_df.groupby("Entity", as_index=False)["Registrations"]
                  .sum().sort_values(by="Registrations", ascending=False).head(10))
        st.dataframe(top_df)

        fig_bar = px.bar(top_df, x="Entity", y="Registrations", title="Top 10 Entities by Registrations")
        st.plotly_chart(fig_bar, use_container_width=True)

if class_files:
    dfs_class = []
    for f in class_files:
        df = load_vahan_file(f)
        if df is not None:
            dfs_class.append(df)
    if dfs_class:
        combined_class_df = pd.concat(dfs_class, ignore_index=True)
        st.subheader("Vehicle-Class Data")
        st.dataframe(combined_class_df.head(20))
