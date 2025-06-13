import os
import pandas as pd
import json
import streamlit as st


@st.cache_data
def load_hale_data(year: int) -> pd.DataFrame | None:
    path = (
        f"./data/IHME_USA_HALE_COUNTY_RACE_ETHNICITY_2009_2019_HALE_BOTH/"
        f"IHME_USA_HALE_COUNTY_RACE_ETHNICITY_2009_2019_HALE_{year}_BOTH_Y2025M03D24.CSV"
    )
    if os.path.exists(path):
        df = pd.read_csv(path)
        df = df[df["fips"].notna()]
        df["fips"] = df["fips"].astype(float).astype(int).astype(str).str.zfill(5)
        return df
    return None

@st.cache_data 
def load_hale_insights() -> dict | None:
    path = "./output/hale-insights.json"

    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)
            return data
    else:
        print("File not found.")
    return None
