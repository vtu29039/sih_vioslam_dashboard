import time
import cv2
import numpy as np
import streamlit as st
from src.camera_stream import CameraStream
from src.dynafusion_engine import DynaFusionEngine
from src.telemetry_controller import TelemetryController

st.set_page_config(
    page_title="SIH VIO-SLAM Vehicle Dashboard", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1f2937; padding: 12px; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

st.title("🚁 Zero-GNSS VIO-SLAM Navigation & Risk Dashboard")
st.caption("Live Field Demonstration — DynaFusion-VIO Dynamic Outlier Rejection Engine")

col1, col2 = st.columns(2)
with col1:
    st.subheader("1. Live Camera Feed (FAST Feature Anchors)")
    frame_spot = st.empty()
with col2:
    st.subheader("2. DynaFusion Dynamic Masking (Dynamic Foliage Red)")
    mask_spot = st.empty()

st.divider()

col3, col4, col5, col6 = st.columns(4)
with col3:
    risk_metric = st.empty()
with col4:
    steer_metric = st.empty()
with col5:
    dist_metric = st.empty()
with col6:
    lat_metric = st.empty()

run = st.checkbox("Initialize Vehicle Camera Loop", value=True)

if run:
    cam = CameraStream()
    engine = DynaFusionEngine()
    controller = TelemetryController()

    while run:
        t0 = time.time()
        frame, gray = cam.get_frame()
        if frame is None:
            st.error("Camera acquisition error.")
            break

        annotated, mask, static_cnt, dyn_pixels, centroid_x = engine.process_frame(frame, gray)
        telemetry = controller.compute_telemetry(dyn_pixels, centroid_x, frame_width=frame.shape1 if hasattr(frame, 'shape1') else frame.shape[1])
        latency_ms = round((time.time() - t0) * 1000, 1)

        frame_spot.image(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB), use_container_width=True)
        mask_spot.image(cv2.cvtColor(mask, cv2.COLOR_BGR2RGB), use_container_width=True)

        risk_metric.metric("Risk Level", telemetry["risk_level"])
        steer_metric.metric(
            "Steering Angle", 
            f"{telemetry['steering_angle']}°", 
            delta="Turn Right" if telemetry['steering_angle'] > 0 else "Turn Left"
        )
        dist_metric.metric("Obstacle Proximity", f"{telemetry['distance_m']} m")
        lat_metric.metric("Loop Latency", f"{latency_ms} ms", delta="50-65 ms target")

    cam.release()
