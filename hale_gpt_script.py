import os
from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd
import itertools
import json


load_dotenv()
print(os.environ.get("OPENAI_API_KEY"))

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# FILE PATH for JSON
hale_insights_path = "./data/hale-insights.json"


def load_hale_data(year):
    path = f"./data/IHME_USA_HALE_COUNTY_RACE_ETHNICITY_2009_2019_HALE_BOTH/IHME_USA_HALE_COUNTY_RACE_ETHNICITY_2009_2019_HALE_{year}_BOTH_Y2025M03D24.CSV"
    if os.path.exists(path):
        df = pd.read_csv(path)
        df = df[df["fips"].notna()]
        df["fips"] = df["fips"].astype(float).astype(int).astype(str).str.zfill(5)
        return df
    return None


def generate_hale_summary(race, age, gender, year, filtered_df):
    """
    Generate a narrative summary from the filtered HALE dataframe.

    Args:
        race (str): Selected race/ethnicity.
        age (str): Selected age group.
        gender (str): Selected gender.
        year (str or int): Selected year.
        filtered_df (pd.DataFrame): Filtered HALE dataset.

    Returns:
        str: A 75-word plain-English summary.
    """
    # 1. National stats
    mean_hale = round(filtered_df["val"].mean(), 2)
    median_hale = round(filtered_df["val"].median(), 2)
    std_hale = round(filtered_df["val"].std(), 2)
    total_counties = filtered_df["fips"].nunique()

    # 2. County-level outliers
    max_row = filtered_df.loc[filtered_df["val"].idxmax()]
    min_row = filtered_df.loc[filtered_df["val"].idxmin()]

    # 3. State trends (approximate via location_name if available)
    state_summary = (
        filtered_df.groupby("location_name")
        .agg(avg_hale=("val", "mean"))
        .sort_values("avg_hale", ascending=False)
        .reset_index()
    )
    top_states = state_summary.head(3)
    bottom_states = state_summary.tail(3)

    # 4. Build prompt
    prompt_text = f"""
You are analyzing a choropleth map showing Healthy Life Expectancy (HALE) across U.S. counties.

Demographic filters:
- Race/Ethnicity: {race}
- Age Group: {age}
- Gender: {gender}
- Year: {year}

National Summary:
- Mean HALE: {mean_hale} years
- Median: {median_hale} years | Std Dev: {std_hale}
- Total Counties Analyzed: {total_counties}

Outliers:
- Highest HALE: {max_row['location_name']} – {round(max_row['val'], 2)} years
- Lowest HALE: {min_row['location_name']} – {round(min_row['val'], 2)} years

Top 3 States by Average HALE:
{top_states.to_string(index=False)}

Bottom 3 States by Average HALE:
{bottom_states.to_string(index=False)}

Write a plain-English summary describing the regional patterns in healthy life expectancy:
- Focus on broad geographic or demographic trends.
- Mention notable disparities.
- Avoid listing raw stats. Write a natural narrative (max 75 words).
"""

    instructions = (
        "You are a skilled health data analyst. "
        "Interpret the choropleth data summary and write a short policy-style paragraph (max 75 words). "
        "Highlight geographic and demographic trends, standout regions, and health disparities. "
        "Do not quote or list numbers. Avoid technical jargon—write clearly for a public health audience."
    )

    try:
        response = client.responses.create(
            model="gpt-4.1",
            instructions=instructions,
            input=prompt_text,
            temperature=0.3,
        )
        return response.output_text
    except Exception as e:
        return f"Error generating HALE summary: {e}"


# Define filter options
race_options = [
    "Total",
    "Latino, Any race",
    "Non-Latino, Black",
    "Non-Latino, White",
    "Non-Latino, American Indian or Alaskan Native",
    "Non-Latino, Asian or Pacific Islander",
]

age_options = [
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
]

gender_options = ["Male", "Female", "Both"]
year_options = [str(y) for y in range(2009, 2020)]

hale_insights_path = "./data/hale-insights.json"

# Generate all filter combinations
combinations = list(
    itertools.product(race_options, age_options, gender_options, year_options)
)

with open(hale_insights_path, "a+") as f:
    for race, age, gender, year in combinations:
        df = load_hale_data(year)
        if df is None:
            print(f"❌ File not found for year {year}")
            continue

        if age == "All Ages":
            filtered_df = (
                df[(df["race_name"] == race) & (df["sex_name"] == gender)]
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
                (df["race_name"] == race)
                & (df["sex_name"] == gender)
                & (df["age_name"] == age)
            ]

        if not filtered_df.empty:
            print(f"\n=== {race} | {age} | {gender} | {year} ===")
            print("Shape:", filtered_df.shape)

            summary_text = generate_hale_summary(
                race=race,
                age=age,
                gender=gender,
                year=year,
                filtered_df=filtered_df,
            )

            print(f"Summary: {summary_text}")

            summary_dict = {f"{race} | {age} | {gender} | {year}": summary_text}
            json.dump(summary_dict, f, indent=2)
            break
        else:
            print(f"\n=== {race} | {age} | {gender} | {year} ===")
            print("⚠️ No data available.")

        # Optional: remove this `break` to generate for all combinations
