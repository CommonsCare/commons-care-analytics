# # from pyrosm import OSM
# import streamlit as st


# @st.cache_data
# def load_hospital_pois():
#     # # osm = OSM("data/health_filtered.osm.pbf")
#     # # pois = osm.get_pois()
#     # pois = pois[pois.geometry.type == "Point"].copy()
#     # pois["lon"] = pois.geometry.x
#     # pois["lat"] = pois.geometry.y
#     return []
import streamlit as st
import pandas as pd
from shapely.geometry import Point


@st.cache_data
def load_hospital_pois():
    # Creating 5 dummy hospital data points
    data = [
        {"name": "City Hospital", "lon": 85.324, "lat": 27.7172, "amenity": "hospital"},
        {"name": "Valley Medical", "lon": 85.310, "lat": 27.7050, "amenity": "clinic"},
        {
            "name": "Himalaya Health Center",
            "lon": 85.330,
            "lat": 27.7205,
            "amenity": "hospital",
        },
        {
            "name": "Sunrise Hospital",
            "lon": 85.340,
            "lat": 27.7155,
            "amenity": "clinic",
        },
        {"name": "Everest Care", "lon": 85.315, "lat": 27.7120, "amenity": "hospital"},
    ]

    # Convert to DataFrame and add geometry column
    df = pd.DataFrame(data)
    df["geometry"] = df.apply(lambda row: Point(row["lon"], row["lat"]), axis=1)

    return df
