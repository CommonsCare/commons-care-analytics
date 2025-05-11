import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px

st.title(
    "United States Healthy Life Expectancy by County, Race, and Ethnicity 2009-2019"
)

st.subheader("Filter")
col1, col2, col3, col4 = st.columns(4)

with col1:
    gender_option = st.selectbox(
        "Gender",
        ("Male", "Female", "Both"),
        index=2,
        placeholder="Select Gender..",
    )

with col2:
    year_option = st.selectbox(
        "Select Year",
        options=[str(year) for year in range(2009, 2020)],
        index=0,
        placeholder="Select Year..",
    )

with col3:
    age_option = st.selectbox(
        "Select Age Group",
        options=[
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
        index=19,
        placeholder="Select Age Group..",
    )

with col4:
    race_option = st.selectbox(
        "Select Race/Ethnicity",
        options=[
            "Total",
            "Latino, Any race",
            "Non-Latino, Black",
            "Non-Latino, White",
            "Non-Latino, American Indian or Alaskan Native",
            "Non-Latino, Asian or Pacific Islander",
        ],
        index=0,
        placeholder="Select Race/Ethnicity..",
    )

st.subheader("Plot")

# Load the data
filename = f"./IHME_USA_HALE_COUNTY_RACE_ETHNICITY_2009_2019_HALE_BOTH/IHME_USA_HALE_COUNTY_RACE_ETHNICITY_2009_2019_HALE_{year_option}_BOTH_Y2025M03D24.CSV"

if os.path.exists(filename):
    df = pd.read_csv(filename)
    st.success(f"Loaded data for year {year_option}")

    # Drop missing or invalid FIPS
    df = df[df["fips"].notna()]

    df["fips"] = df["fips"].astype(float).astype(int).astype(str).str.zfill(5)

    if age_option == "All Ages":
        filtered_df = df[
            (df["race_name"] == race_option) & (df["sex_name"] == gender_option)
        ]

        filtered_df = (
            filtered_df.groupby("fips")
            .agg(
                {
                    "val": "mean",
                    "upper": "mean",
                    "lower": "mean",
                    "location_name": "first",  # Take the first name per fips
                }
            )
            .reset_index()
        )

    else:
        # Filter based on selections
        filtered_df = df[
            (df["race_name"] == race_option)
            & (df["sex_name"] == gender_option)
            & (df["age_name"] == age_option)
        ]

    if not filtered_df.empty:
        st.subheader("🧪 Filtered Data Preview")
        # Choropleth Map

        # Create enhanced choropleth map
        fig = px.choropleth(
            filtered_df,
            geojson="https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json",
            locations="fips",
            color="val",
            color_continuous_scale="Cividis",  # Modern, clean color palette
            range_color=(filtered_df["val"].min(), filtered_df["val"].max()),
            scope="usa",
            labels={"val": "HALE (Years)"},
            hover_data={
                "location_name": True,
                "val": ":.2f",
                "upper": ":.2f",
                "lower": ":.2f",
                "fips": False,  # Hide FIPS in tooltip
            },
        )

        # Update layout for better visuals
        fig.update_layout(
            title={
                "text": f"<b>Healthy Life Expectancy (HALE)</b><br>{race_option} | {age_option} | {gender_option} | {year_option}",
                "y": 0.92,
                "x": 0.5,
                "xanchor": "center",
                "yanchor": "top",
            },
            font=dict(family="Arial", size=14),
            geo=dict(
                lakecolor="white",
                showland=True,
                landcolor="lightgray",
                showcountries=False,
                showlakes=True,
                subunitcolor="white",
                showcoastlines=False,
            ),
            margin=dict(l=0, r=0, t=100, b=0),
            coloraxis_colorbar=dict(title="Years", tickformat=".1f"),
        )

        # Display the figure
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available for the selected filters.")

else:
    st.error(f"Data file for year {year_option} not found: {filename}")
