from pyrosm import OSM
import streamlit as st


@st.cache_data
def load_hospital_pois():
    osm = OSM("data/health_filtered.osm.pbf")
    pois = osm.get_pois()
    pois = pois[pois.geometry.type == "Point"].copy()
    pois["lon"] = pois.geometry.x
    pois["lat"] = pois.geometry.y
    return pois
