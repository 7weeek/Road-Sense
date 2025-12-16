# main.py
import streamlit as st
from PIL import Image
import numpy as np

from route_planner import render_route_planner


from inference import (
    load_models,
    predict_fog,
    predict_accident,
    detect_vehicles
)

from risk_map import render_risk_maps

# ---------------- PAGE CONFIG (ONLY HERE) ----------------
st.set_page_config(
    page_title="Road Risk Analyzer",
    layout="wide"
)

st.title("🚦 Road Risk Analyzer")

# ---------------- TABS ----------------
tab1, tab2, tab3 = st.tabs(["Image Analysis", "Risk Maps", "Route Planner"])




# ======================================================
# TAB 1 : IMAGE ANALYSIS
# ======================================================
with tab1:
    @st.cache_resource
    def init_models():
        return load_models()

    fog_model, accident_model, yolo_model = init_models()

    uploaded = st.file_uploader(
        "Upload a road image",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded:
        img_pil = Image.open(uploaded).convert("RGB")
        img_np = np.array(img_pil)

        col1, col2 = st.columns(2)

        with col1:
            st.image(img_pil, caption="Uploaded Image", use_container_width=True)

            with st.spinner("Analyzing road conditions..."):
                fog_status = predict_fog(fog_model, img_pil)
                accident_status = predict_accident(accident_model, img_pil)

        with col2:
            st.subheader("🧠 Analysis Results")
            st.metric("🌫 Weather", fog_status)
            st.metric("🚨 Accident Risk", accident_status)

            results, vehicle_counts = detect_vehicles(yolo_model, img_np)

            st.subheader("🚗 Vehicle Count")
            if vehicle_counts:
                for k, v in vehicle_counts.items():
                    st.write(f"**{k}** : {v}")
            else:
                st.write("No vehicles detected")

        if results is not None:
            st.subheader("📦 Vehicle Detection")
            st.image(results.plot(), use_container_width=True)

# ======================================================
# TAB 2 : MAPS
# ======================================================
with tab2:
    render_risk_maps()

with tab3:
    render_route_planner()
