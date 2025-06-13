import streamlit as st
import plotly.express as px
from src.utils.sahie_data import load_sahie_data, load_sahie_insights
from src.utils.sahie_options import SEX_MAP, AGE_MAP, INCOME_MAP


def render():
    df = load_sahie_data()
    if df is None:
        st.error("SAHIE 2022 data not found.")
        return

    fc1, fc2, fc3 = st.columns(3)

    with fc1:
        selected_sex = st.selectbox("Sex", list(SEX_MAP.values()), index=0)
        st.session_state["selected_sex"] = selected_sex

    with fc2:
        selected_age = st.selectbox("Age Group", list(AGE_MAP.values()), index=0)
        st.session_state["selected_age"] = selected_age

    with fc3:
        selected_income = st.selectbox(
            "Income Level", list(INCOME_MAP.values()), index=0
        )
        st.session_state["selected_income"] = selected_income

    sex_code = [k for k, v in SEX_MAP.items() if v == selected_sex][0]
    age_code = [k for k, v in AGE_MAP.items() if v == selected_age][0]
    income_code = [k for k, v in INCOME_MAP.items() if v == selected_income][0]

    filtered_df = df[
        (df["sexcat"] == sex_code)
        & (df["agecat"] == age_code)
        & (df["iprcat"] == income_code)
    ]

    if filtered_df.empty:
        st.warning("No data available for selected filters.")
        return

    summary = (
        filtered_df.groupby("fips")
        .agg(
            {
                "PCTUI": "mean",
                "county_name": "first",
                "state_name": "first",
            }
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


def render_insight():
    insights = load_sahie_insights()
    if not insights:
        st.error("SAHIE insights not found.")
        return

    selected_sex = st.session_state.get("selected_sex", "Both")
    selected_age = st.session_state.get("selected_age", "Under 65")
    selected_income = st.session_state.get("selected_income", "All incomes")

    key = f"{selected_sex} | {selected_age} | {selected_income}"

    st.markdown(f"**Filter:** `{key}`")
    st.markdown(insights.get(key, "No insight available for the selected filters."))
