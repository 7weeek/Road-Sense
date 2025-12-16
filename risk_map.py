# risk_map.py
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

CSV_PATH = "road_events_delhi_ncr.csv"

def render_risk_maps():
    st.header("🗺️ Road Risk Heatmaps")

    df = pd.read_csv(CSV_PATH)

    center = [df.latitude.mean(), df.longitude.mean()]

    subtab1, subtab2, subtab3, subtab4 = st.tabs([
        "🌫 Fog Map",
        "🚨 Accident Map",
        "🚗 Traffic Map",
        "🧠 Combined Risk"
    ])

    # ================= FOG MAP =================
    with subtab1:
        fog_map = folium.Map(location=center, zoom_start=11)

        for _, row in df.iterrows():
            if row["fog"] == "Foggy":
                folium.CircleMarker(
                    location=[row.latitude, row.longitude],
                    radius=10,
                    color="blue",
                    fill=True,
                    fill_opacity=0.3
                ).add_to(fog_map)

        st_folium(fog_map, use_container_width=True, height=550)

    # ================= ACCIDENT MAP =================
    with subtab2:
        accident_map = folium.Map(location=center, zoom_start=11)

        for _, row in df.iterrows():
            if row["accident"] == "Accident":
                folium.Marker(
                    location=[row.latitude, row.longitude],
                    icon=folium.Icon(color="red", icon="warning-sign"),
                    popup="Accident Reported"
                ).add_to(accident_map)

        st_folium(accident_map, use_container_width=True, height=550)

    # ================= TRAFFIC MAP =================
    with subtab3:
        traffic_map = folium.Map(location=center, zoom_start=11)

        for _, row in df.iterrows():
            count = row.vehicle_count

            if count < 10:
                color = "green"
            elif count < 25:
                color = "orange"
            else:
                color = "red"

            folium.CircleMarker(
                location=[row.latitude, row.longitude],
                radius=8,
                color=color,
                fill=True,
                fill_opacity=0.6,
                popup=f"Vehicles: {count}"
            ).add_to(traffic_map)

        st_folium(traffic_map, use_container_width=True, height=550)

    # ================= COMBINED RISK =================
    with subtab4:
        combined_map = folium.Map(location=center, zoom_start=11)

        for _, row in df.iterrows():
            risk_score = 0
            if row.fog == "Foggy":
                risk_score += 1
            if row.accident == "Accident":
                risk_score += 2
            if row.vehicle_count > 20:
                risk_score += 1

            if risk_score >= 3:
                color = "darkred"
            elif risk_score == 2:
                color = "red"
            elif risk_score == 1:
                color = "orange"
            else:
                color = "green"

            folium.CircleMarker(
                location=[row.latitude, row.longitude],
                radius=9,
                color=color,
                fill=True,
                fill_opacity=0.7,
                popup=f"Risk Score: {risk_score}"
            ).add_to(combined_map)

        st_folium(combined_map, use_container_width=True, height=550)
