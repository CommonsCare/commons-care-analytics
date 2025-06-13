import os
import pandas as pd
import streamlit as st
import json


@st.cache_data
def load_sahie_data():
    path = "./data/sahie-2022-csv/sahie_2022.csv"
    if os.path.exists(path):
        df = pd.read_csv(path)
        df = df[df["geocat"] == 50].copy()
        df["fips"] = df["statefips"].astype(str).str.zfill(2) + df["countyfips"].astype(
            str
        ).str.zfill(3)
        df["PCTUI"] = pd.to_numeric(df["PCTUI"], errors="coerce")
        return df.dropna(subset=["PCTUI"])
    return None


@st.cache_data
def load_sahie_insights():
    path = "./output/sahie-insights.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return None
