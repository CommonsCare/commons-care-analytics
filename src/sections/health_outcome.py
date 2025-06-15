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
    with st.container(key="hale_container"):
        st.markdown(
            """
            <h3>Healthy Life Expectancy (HALE)</h3>
            <p>HALE is a measure of the average number of years that a person can expect to live in good health, taking into account mortality and morbidity.</p>
            """,
            unsafe_allow_html=True,
        )
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
                        "text": f"Healthy Life Expectancy (HALE)<br>{race_option} | {age_option} | {gender_option} | {year_option}",
                        "x": 0.5,
                        "xanchor": "center",
                    },
                    font=dict(family="Arial", size=14),
                    geo=dict(
                        lakecolor="white",
                        showland=True,
                        landcolor="white",
                        showcountries=False,
                        showlakes=True,
                    ),
                    margin=dict(l=0, r=0, t=100, b=0),
                    coloraxis_colorbar=dict(title="Years", tickformat=".1f"),
                    plot_bgcolor="white",  # White background inside the plotting area
                    paper_bgcolor="white",  # White background outside the plotting area
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

    display_text = ""

    if insights is None:
        display_text = "Insights file not found or failed to load."
    elif key in insights:
        display_text = insights[key]
    else:
        display_text = "Insights not found for given data."

    st.markdown(
        f"""
    <div class="insight-card">
        <h4>Commons-Care Insights </h4>
        <div class="key-panel-header">
            Generated Key:
            <span class="key-panel-tags">
                <span>{race_option}</span>
                <span>{age_option}</span>
                <span>{gender_option}</span>
                <span>{year_option}</span>
            </span>
        </div>
        <div class="key-panel-content">
            {display_text}
        </div>
        <div class="panel-message">
            This panel provides data-driven summaries generated by AI.
        </div>
        <div class="panel-footer">
            Generated by Commons-Care AI
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )
