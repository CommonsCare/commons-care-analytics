import streamlit as st
import plotly.express as px
from src.utils.hale_data import load_hale_data
from src.utils.hale_insights import load_hale_insights
from src.utils.hale_options import (
    GENDER_OPTIONS,
    YEAR_OPTIONS,
    AGE_OPTIONS,
    RACE_OPTIONS,
)


def render():
    fc1, fc2, fc3, fc4 = st.columns(4)

    with fc1:
        gender_option = st.selectbox("Gender", GENDER_OPTIONS, index=2)
        st.session_state["gender_option"] = gender_option

    with fc2:
        year_option = st.selectbox("Select Year", YEAR_OPTIONS, index=0)
        st.session_state["year_option"] = year_option

    with fc3:
        age_option = st.selectbox("Select Age Group", AGE_OPTIONS, index=0)
        st.session_state["age_option"] = age_option

    with fc4:
        race_option = st.selectbox("Select Race/Ethnicity", RACE_OPTIONS, index=0)
        st.session_state["race_option"] = race_option

    df = load_hale_data(year_option)
    if df is not None:
        if age_option == "All Ages":
            filtered_df = (
                df[(df["race_name"] == race_option) & (df["sex_name"] == gender_option)]
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
                    "text": f"Healthy Life Expectancy (HALE)<br>{race_option} | {age_option} | {gender_option} | {year_option}",
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
            st.warning("No data available for the selected filters.")
    else:
        st.error("HALE dataset not found.")


def render_insight():
    insights = load_hale_insights()

    gender_option = st.session_state.get("gender_option", "Both")
    year_option = st.session_state.get("year_option", "2009")
    age_option = st.session_state.get("age_option", "<1 year")
    race_option = st.session_state.get("race_option", "Total")

    key = f"{race_option} | {age_option} | {gender_option} | {year_option}"

    print("Current insight key:", key)
    st.markdown(f"**Generated Key:** `{key}`")

    if insights is None:
        st.error("Insights file not found or failed to load.")
    elif key in insights:
        st.markdown(insights[key])
    else:
        st.warning("Insights not found for given data.")
