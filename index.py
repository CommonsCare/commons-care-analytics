import streamlit as st
import pandas as pd
import os
import plotly.express as px
from pyrosm import OSM
import json

st.set_page_config(layout="wide")

# --- Improved CSS Styling ---
st.markdown(
    """
<style>
/* Compact layout */
.css-18e3th9, .css-1d391kg, .block-container {
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
    padding-left: 1rem;
    padding-right: 1rem;
}
.css-1kyxreq {
    padding: 0rem 0.5rem;
}
h1, h2, h3, h4 {
    margin-bottom: 0.4rem;
    color: #2c3e50;
}

/* Button styling */
div.stButton > button {
    border: 2px solid #34495e;
    background-color: #ecf0f1;
    color: #2c3e50;
    padding: 6px 12px;
    border-radius: 0px;
    font-weight: 600;
    transition: background-color 0.2s ease-in-out, color 0.2s ease-in-out;
}
div.stButton > button:hover {
    background-color: #d0d3d4;
    color: #000;
}
div.stButton > button:active {
    background-color: #bfc9ca;
    border-color: #2c3e50;
    color: #000;
}
div.stButton > button:disabled {
    background-color: #f4f6f7 !important;
    color: #aaa !important;
    border: 2px solid #ccc !important;
    cursor: not-allowed !important;
    opacity: 0.6;
}

/* Tooltip styling */
[data-testid="stTooltip"] {
    background-color: #2c3e50;
    color: white;
    font-size: 0.9rem;
}
</style>
""",
    unsafe_allow_html=True,
)


# Initialize session state
def initialize_state():
    if "selected_goal" not in st.session_state:
        st.session_state.selected_goal = "Access"


initialize_state()


# --- Loaders ---
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
        return df.dropna(subset=["PCTUI"])
    return None


@st.cache_data
def load_sahie_insights():
    path = "./data/sahie-insights.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return None


@st.cache_data
def load_hale_insights():
    path = "./data/hale-insights.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return None


@st.cache_data
def load_hospital_pois(pbf_path):
    osm = OSM(pbf_path)
    pois = osm.get_pois()
    pois = pois[pois.geometry.type == "Point"].copy()
    pois["lon"] = pois.geometry.x
    pois["lat"] = pois.geometry.y
    return pois


# --- Title ---
with st.container():
    st.title("🌐 System Goals Dashboard")
    st.markdown("---")

# --- Layout ---
col1, col_div1, col2, col_div2, col3 = st.columns([0.7, 0.05, 3, 0.05, 1])
# --- Intermediate Goals Panel ---
with col1:
    st.markdown("### 🎯 Intermediate Goals")
    if st.button("Access", use_container_width=True):
        st.session_state.selected_goal = "Access"
    st.button("Quality", disabled=True, use_container_width=True)
    st.button("Efficiency", disabled=True, use_container_width=True)
    st.button("Equity", disabled=True, use_container_width=True)

# Divider 1
with col_div1:
    st.markdown(
        "<div style='height: 320px; border-left: 1px solid gray;'></div>",
        unsafe_allow_html=True,
    )

# --- System Goal Selector ---
with col2:
    st.markdown("### 🔘 Select System Goal")
    b1, _, b2, _, b3 = st.columns([1, 0.025, 1, 0.025, 1])
    with b1:
        if st.button("Health Outcome", use_container_width=True):
            st.session_state.selected_goal = "Health Outcome"
    with b2:
        st.button("Customer Satisfaction", disabled=True, use_container_width=True)
    with b3:
        if st.button("Financial Risk Protection", use_container_width=True):
            st.session_state.selected_goal = "Financial Risk Protection"
    st.markdown("---")
    st.markdown(f"**Currently Viewing:** `{st.session_state.selected_goal}`")

    # Health Outcome Panel
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

    elif st.session_state.selected_goal == "Access":
        st.success("Access panel is under construction.")
        pois = load_hospital_pois("health_filtered.osm.pbf")
        HEALTH_AMENITIES = {
            "hospital": "🏥 Hospital",
            "clinic": "🏨 Clinic",
            "doctors": "👨‍⚕️ Doctor",
            "dentist": "🦷 Dentist",
            "pharmacy": "💊 Pharmacy",
            "nursing_home": "🏡 Nursing Home",
            "rehabilitation": "🧠 Rehabilitation",
            "birthing_center": "🤱 Birthing Center",
            "alternative": "🌿 Alternative Medicine",
            "physiotherapist": "🏃 Physiotherapy",
            "psychotherapist": "🧘 Psychotherapy",
            "healthcare": "🏪 Healthcare (Unspecified)",
            "first_aid": "🩹 First Aid",
            "blood_donation": "🩸 Blood Donation",
        }
        selected_amenities = st.multiselect(
            "Select health amenities to display",
            options=list(HEALTH_AMENITIES.keys()),
            format_func=lambda x: HEALTH_AMENITIES[x],
            default=["hospital", "clinic"],
        )
        filtered_pois = pois[pois["amenity"].isin(selected_amenities)]
        filtered_pois["icon_label"] = filtered_pois["amenity"].map(HEALTH_AMENITIES)

        fig = px.scatter_mapbox(
            filtered_pois,
            lat="lat",
            lon="lon",
            color="amenity",
            hover_name="name",
            hover_data={"amenity": True, "lat": False, "lon": False},
            zoom=3,
            height=800,
            color_discrete_sequence=px.colors.qualitative.Safe,
        )
        fig.update_layout(
            mapbox_style="carto-positron",
            margin={"r": 10, "t": 10, "l": 10, "b": 10},
            legend=dict(
                title="Amenity Type",
                orientation="v",
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                font=dict(size=12),
                bgcolor="rgba(255,255,255,0.7)",
            ),
            font=dict(family="Arial", size=14),
        )
        st.plotly_chart(fig, use_container_width=True)

# Divider 2
with col_div2:
    st.markdown(
        "<div style='height: 320px; border-left: 1px solid gray;'></div>",
        unsafe_allow_html=True,
    )

# --- AI Insights Panel ---
with col3:
    st.markdown("### 💡 AI Insights")
    if st.session_state.selected_goal == "Health Outcome":
        insights = load_hale_insights()
        if insights:
            key = f"{race_option} | {age_option} | {gender_option} | {year_option}"
            st.markdown(f"**Filter:** `{key}`")
            st.markdown(
                insights.get(key, "No insight available for the selected filters.")
            )
    elif st.session_state.selected_goal == "Financial Risk Protection":
        insights = load_sahie_insights()
        if insights:
            key = f"{selected_sex} | {selected_age} | {selected_income}"
            st.markdown(f"**Filter:** `{key}`")
            st.markdown(
                insights.get(key, "No insight available for the selected filters.")
            )
    st.info("This is the AI-generated insight panel.")
    st.markdown("_Generated by Commons-Care AI_")

# --- Control Knobs ---
st.markdown("---")
knob_cols = st.columns(5)
for col, label in zip(
    knob_cols, ["Financing", "Behavior", "Organization", "Regulation", "Payment"]
):
    with col:
        st.button(
            label, disabled=True, help="Feature coming soon", use_container_width=True
        )
st.markdown(
    "<h3 style='text-align: center;'>🛠️ Control Knobs</h3>", unsafe_allow_html=True
)
