import streamlit as st
import pandas as pd
import os
import plotly.express as px

st.set_page_config(layout="wide")


# Initialize session state
def initialize_state():
    if "selected_goal" not in st.session_state:
        st.session_state.selected_goal = "Financial Risk Protection"


initialize_state()


# Cached data loaders
@st.cache_data
def load_hale_data(year):
    path = f"./data/IHME_USA_HALE_COUNTY_RACE_ETHNICITY_2009_2019_HALE_BOTH/IHME_USA_HALE_COUNTY_RACE_ETHNICITY_2009_2019_HALE_{year}_BOTH_Y2025M03D24.CSV"
    if os.path.exists(path):
        df = pd.read_csv(path)
        df = df[df["fips"].notna()]
        df["fips"] = df["fips"].astype(float).astype(int).astype(str).str.zfill(5)
        return df
    return None


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
        df = df.dropna(subset=["PCTUI"])
        return df
    return None


# Title
st.title("🌐 System Goals Dashboard")
st.markdown("---")

# Layout
col1, col_div1, col2, col_div2, col3 = st.columns([0.7, 0.05, 3, 0.05, 1])

# Intermediate Goals (left)
with col1:
    st.markdown("### 🎯 Intermediate Goals")
    for label in ["Access", "Quality", "Efficiency", "Equity"]:
        st.button(
            label,
            disabled=True,
            use_container_width=True,
            help="Option currently unavailable",
        )

# Divider 1
with col_div1:
    st.markdown(
        "<div style='height: 320px; border-left: 1px solid gray;'></div>",
        unsafe_allow_html=True,
    )

# System Goal Selector (center)
with col2:
    st.markdown("### 🔘 Select System Goal")
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("Health Outcome"):
            st.session_state.selected_goal = "Health Outcome"
    with b2:
        st.button(
            "Customer Satisfaction", disabled=True, help="Option currently unavailable"
        )
    with b3:
        if st.button("Financial Risk Protection"):
            st.session_state.selected_goal = "Financial Risk Protection"

    st.markdown("---")
    st.markdown(f"**Currently Viewing:** `{st.session_state.selected_goal}`")

    # HEALTH OUTCOME PANEL
    if st.session_state.selected_goal == "Health Outcome":
        fc1, fc2, fc3, fc4 = st.columns(4)
        with fc1:
            gender_option = st.selectbox("Gender", ("Male", "Female", "Both"), index=2)
        with fc2:
            year_option = st.selectbox(
                "Select Year", [str(y) for y in range(2009, 2020)], index=0
            )
        with fc3:
            age_option = st.selectbox(
                "Select Age Group",
                [
                    "<1 year",
                    "1 to 4",
                    "5 to 9",
                    "10 to 14",
                    "15 to 19",
                    "20 to 24",
                    "25 to 29",
                    "30 to 34",
                    "35 to 39",
                    "40 to 44",
                    "45 to 49",
                    "50 to 54",
                    "55 to 59",
                    "60 to 64",
                    "65 to 69",
                    "70 to 74",
                    "75 to 79",
                    "80 to 84",
                    "85 plus",
                    "All Ages",
                ],
                index=0,
            )
        with fc4:
            race_option = st.selectbox(
                "Select Race/Ethnicity",
                [
                    "Total",
                    "Latino, Any race",
                    "Non-Latino, Black",
                    "Non-Latino, White",
                    "Non-Latino, American Indian or Alaskan Native",
                    "Non-Latino, Asian or Pacific Islander",
                ],
                index=0,
            )

        df = load_hale_data(year_option)
        if df is not None:
            if age_option == "All Ages":
                filtered_df = (
                    df[
                        (df["race_name"] == race_option)
                        & (df["sex_name"] == gender_option)
                    ]
                    .groupby("fips")
                    .agg(
                        {
                            "val": "mean",
                            "upper": "mean",
                            "lower": "mean",
                            "location_name": "first",
                        }
                    )
                    .reset_index()
                )
            else:
                filtered_df = df[
                    (df["race_name"] == race_option)
                    & (df["sex_name"] == gender_option)
                    & (df["age_name"] == age_option)
                ]

            if not filtered_df.empty:
                fig = px.choropleth(
                    filtered_df,
                    geojson="https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json",
                    locations="fips",
                    color="val",
                    color_continuous_scale="Cividis",
                    range_color=(filtered_df["val"].min(), filtered_df["val"].max()),
                    scope="usa",
                    labels={"val": "HALE (Years)"},
                    hover_data={
                        "location_name": True,
                        "val": ":.2f",
                        "upper": ":.2f",
                        "lower": ":.2f",
                        "fips": False,
                    },
                )
                fig.update_layout(
                    title={
                        "text": f"<b>Healthy Life Expectancy (HALE)</b><br>{race_option} | {age_option} | {gender_option} | {year_option}",
                        "x": 0.5,
                        "xanchor": "center",
                    },
                    font=dict(family="Arial", size=14),
                    geo=dict(
                        lakecolor="white",
                        showland=True,
                        landcolor="lightgray",
                        showcountries=False,
                        showlakes=True,
                    ),
                    margin=dict(l=0, r=0, t=100, b=0),
                    coloraxis_colorbar=dict(title="Years", tickformat=".1f"),
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ No data available for the selected filters.")
        else:
            st.error("❌ HALE dataset not found.")

    # FINANCIAL RISK PROTECTION PANEL
    elif st.session_state.selected_goal == "Financial Risk Protection":
        sahie_df = load_sahie_data()

        sex_map = {0: "Both", 1: "Male", 2: "Female"}
        age_map = {
            0: "Under 65",
            1: "18 to 64",
            2: "40 to 64",
            3: "50 to 64",
            4: "Under 19",
            5: "21 to 64",
        }
        income_map = {
            0: "All incomes",
            1: "≤ 200% poverty",
            2: "≤ 250%",
            3: "≤ 138%",
            4: "≤ 400%",
            5: "138% – 400%",
        }

        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            selected_sex = st.selectbox("Sex", list(sex_map.values()), index=0)
        with fc2:
            selected_age = st.selectbox("Age Group", list(age_map.values()), index=0)
        with fc3:
            selected_income = st.selectbox(
                "Income Level", list(income_map.values()), index=0
            )

        sex_code = [k for k, v in sex_map.items() if v == selected_sex][0]
        age_code = [k for k, v in age_map.items() if v == selected_age][0]
        income_code = [k for k, v in income_map.items() if v == selected_income][0]

        if sahie_df is not None:
            filtered_df = sahie_df[
                (sahie_df["sexcat"] == sex_code)
                & (sahie_df["agecat"] == age_code)
                & (sahie_df["iprcat"] == income_code)
            ]

            if not filtered_df.empty:
                summary = (
                    filtered_df.groupby("fips")
                    .agg(
                        {"PCTUI": "mean", "county_name": "first", "state_name": "first"}
                    )
                    .reset_index()
                )

                title_filters = f"{selected_sex} | {selected_age} | {selected_income}"

                fig = px.choropleth(
                    summary,
                    geojson="https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json",
                    locations="fips",
                    color="PCTUI",
                    color_continuous_scale="Reds",
                    scope="usa",
                    labels={"PCTUI": "% Uninsured"},
                    hover_data=["state_name", "county_name", "PCTUI"],
                )
                fig.update_layout(
                    title={
                        "text": f"<b>Uninsured % by County</b><br>{title_filters} – SAHIE 2022",
                        "x": 0.5,
                        "xanchor": "center",
                    },
                    geo=dict(
                        lakecolor="white",
                        landcolor="lightgray",
                        showlakes=True,
                        showcoastlines=False,
                    ),
                    margin=dict(l=0, r=0, t=100, b=0),
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ No data available for selected filters.")
        else:
            st.error("❌ SAHIE 2022 data not found.")

# Divider 2
with col_div2:
    st.markdown(
        "<div style='height: 320px; border-left: 1px solid gray;'></div>",
        unsafe_allow_html=True,
    )

# Insights panel (right)
with col3:
    st.markdown("### 💡 AI Insights")
    st.info("This is the AI-generated insight panel.")
    st.markdown("_Generated by Commons-Care AI_")

# Control Knobs (bottom)
st.markdown("---")
st.markdown(
    "<h3 style='text-align: center;'>🛠️ Control Knobs</h3>", unsafe_allow_html=True
)
knob_cols = st.columns(5)
for col, label in zip(
    knob_cols, ["Financing", "Behavior", "Organization", "Regulation", "Payment"]
):
    with col:
        st.button(label, disabled=True, help="Feature coming soon")
