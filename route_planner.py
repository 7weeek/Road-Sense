# route_planner.py
import streamlit as st
import folium
import requests
from streamlit_folium import st_folium

# ---------------- DELHI NCR BOUNDING BOX ----------------
DELHI_NCR_BOUNDS = {
    "lat_min": 28.40,
    "lat_max": 28.90,
    "lon_min": 76.80,
    "lon_max": 77.50
}

# ---------------- HELPERS ----------------
def is_within_delhi_ncr(lat, lon):
    return (
        DELHI_NCR_BOUNDS["lat_min"] <= lat <= DELHI_NCR_BOUNDS["lat_max"]
        and DELHI_NCR_BOUNDS["lon_min"] <= lon <= DELHI_NCR_BOUNDS["lon_max"]
    )


def get_osrm_route(src_lat, src_lon, dst_lat, dst_lon):
    """
    Calls OSRM public API to get best driving route
    """
    url = (
        f"http://router.project-osrm.org/route/v1/driving/"
        f"{src_lon},{src_lat};{dst_lon},{dst_lat}"
        f"?overview=full&geometries=geojson"
    )

    r = requests.get(url, timeout=10)
    if r.status_code != 200:
        return None

    data = r.json()
    if data.get("code") != "Ok":
        return None

    route = data["routes"][0]
    coords = route["geometry"]["coordinates"]  # lon, lat
    distance_km = route["distance"] / 1000
    duration_min = route["duration"] / 60

    return coords, distance_km, duration_min


# ---------------- STREAMLIT UI ----------------
def render_route_planner():
    st.subheader("🛣 Route Planner (Delhi-NCR)")

    st.caption(
        "Enter two locations within Delhi-NCR to find the best road route."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📍 Source Location")
        src_lat = st.number_input("Source Latitude", value=28.6139, format="%.6f")
        src_lon = st.number_input("Source Longitude", value=77.2090, format="%.6f")

    with col2:
        st.markdown("### 🎯 Destination Location")
        dst_lat = st.number_input("Destination Latitude", value=28.7041, format="%.6f")
        dst_lon = st.number_input("Destination Longitude", value=77.1025, format="%.6f")

    if st.button("🚀 Find Best Route"):
        # ---------------- VALIDATION ----------------
        if not is_within_delhi_ncr(src_lat, src_lon):
            st.error("Source location is outside Delhi-NCR bounds.")
            return

        if not is_within_delhi_ncr(dst_lat, dst_lon):
            st.error("Destination location is outside Delhi-NCR bounds.")
            return

        with st.spinner("Finding best route..."):
            result = get_osrm_route(src_lat, src_lon, dst_lat, dst_lon)

        if result is None:
            st.error("Unable to fetch route. Please try again.")
            return

        coords, distance_km, duration_min = result

        # ---------------- MAP ----------------
        center_lat = (src_lat + dst_lat) / 2
        center_lon = (src_lon + dst_lon) / 2

        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=12,
            tiles="OpenStreetMap"
        )

        # Start marker
        folium.Marker(
            [src_lat, src_lon],
            popup="Source",
            icon=folium.Icon(color="green", icon="play")
        ).add_to(m)

        # End marker
        folium.Marker(
            [dst_lat, dst_lon],
            popup="Destination",
            icon=folium.Icon(color="red", icon="stop")
        ).add_to(m)

        # Route line
        latlon_coords = [[lat, lon] for lon, lat in coords]
        folium.PolyLine(
            latlon_coords,
            color="blue",
            weight=5,
            opacity=0.8
        ).add_to(m)

        # ---------------- METRICS ----------------
        st.success("Route found successfully")

        c1, c2 = st.columns(2)
        c1.metric("📏 Distance (km)", f"{distance_km:.2f}")
        c2.metric("⏱ Estimated Time (min)", f"{duration_min:.1f}")

        st_folium(m, width=1100, height=600)
