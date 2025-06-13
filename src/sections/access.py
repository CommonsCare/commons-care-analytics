import streamlit as st
import plotly.express as px
from src.utils.health_access_pois import load_hospital_pois


def render():
    st.markdown("#### Access to Health Amenities")

    pois = load_hospital_pois()

    HEALTH_AMENITIES = {
        "hospital": "Hospital",
        "clinic": "Clinic",
        "doctors": "Doctor",
        "dentist": "Dentist",
        "pharmacy": "Pharmacy",
        "nursing_home": "Nursing Home",
        "rehabilitation": "Rehabilitation",
        "birthing_center": "Birthing Center",
        "alternative": "Alternative Medicine",
        "physiotherapist": "Physiotherapy",
        "psychotherapist": "Psychotherapy",
        "healthcare": "Healthcare (Unspecified)",
        "first_aid": "First Aid",
        "blood_donation": "Blood Donation",
    }

    selected_amenities = st.multiselect(
        "Select health amenities to display",
        options=list(HEALTH_AMENITIES.keys()),
        format_func=lambda x: HEALTH_AMENITIES[x],
        default=["hospital", "clinic"],
    )

    filtered_pois = pois[pois["amenity"].isin(selected_amenities)]
    filtered_pois["label"] = filtered_pois["amenity"].map(HEALTH_AMENITIES)

    fig = px.scatter_mapbox(
        filtered_pois,
        lat="lat",
        lon="lon",
        color="amenity",
        hover_name="name",
        hover_data={"amenity": True, "lat": False, "lon": False},
        zoom=3,
        height=750,
        color_discrete_sequence=px.colors.qualitative.Safe,
    )

    fig.update_layout(
        mapbox_style="carto-positron",
        margin={"r": 10, "t": 10, "l": 10, "b": 10},
        legend=dict(
            title="Amenity Type",
            orientation="v",
            yanchor="top",
            y=0.98,
            xanchor="left",
            x=0.01,
            font=dict(size=12),
            bgcolor="rgba(255,255,255,0.8)",
        ),
        font=dict(family="Arial", size=13),
    )

    st.plotly_chart(fig, use_container_width=True)
