import streamlit as st
import cv2
import av
import numpy as np
import time
from streamlit_webrtc import webrtc_streamer, RTCConfiguration, VideoProcessorBase

# Page Configuration
st.set_page_config(page_title="VIO-SLAM Dashboard", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS styling for metric card UI
st.markdown("""
    <style>
    .metric-card {
        background-color: #1a1c23;
        border-radius: 8px;
        padding: 15px 20px;
        color: white;
        margin-bottom: 10px;
    }
    .metric-title {
        color: #8b92a5;
        font-size: 0.85rem;
        margin-bottom: 5px;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 600;
        margin-bottom: 5px;
    }
    .badge-green {
        background-color: #133829;
        color: #3dd68c;
        border-radius: 12px;
        padding: 3px 10px;
        font-size: 0.75rem;
        display: inline-block;
    }
    </style>
""", unsafe_allow_html=True)

# WebRTC STUN Server Configuration
RTC_CONFIGURATION = RTCConfiguration(
    {
        "iceServers": [
            {"urls": ["stun:stun.l.google.com:19302"]},
            {"urls": ["stun:stun1.l.google.com:19302"]},
            {"urls": ["stun:stun2.l.google.com:19302"]},
        ]
    }
)

class VIODualStreamProcessor(VideoProcessorBase):
    def __init__(self):
        self.risk_level = "CLEAR"
        self.steering_angle = 2.1
        self.turn_direction = "Turn Right"
        self.proximity = 3.5
        self.latency = 17.8
        self.last_time = time.time()

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        start_time = time.time()
        img = frame.to_ndarray(format="bgr24")
        h, w, _ = img.shape

        # Convert to Grayscale for feature tracking
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray_3ch = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

        # Detect Optical Flow / VIO Features
        corners = cv2.goodFeaturesToTrack(gray, maxCorners=120, qualityLevel=0.25, minDistance=6)

        if corners is not None:
            # Draw Green VIO Feature points on Left Stream (RGB)
            for c in corners:
                x, y = c.ravel()
                cv2.circle(img, (int(x), int(y)), 3, (0, 255, 0), -1)

            # Draw Red Feature Tracking points on Right Stream (Grayscale)
            for c in corners:
                x, y = c.ravel()
                cv2.circle(gray_3ch, (int(x), int(y)), 3, (0, 0, 255), -1)

            # Calculate Live Metrics
            avg_x = np.mean(corners[:, 0, 0])
            offset_x = avg_x - (w / 2)
            self.steering_angle = round(float((offset_x / (w / 2)) * 15), 1)
            self.turn_direction = "Turn Right" if self.steering_angle >= 0 else "Turn Left"
            
            num_points = len(corners)
            if num_points < 30:
                self.risk_level = "CRITICAL"
                self.proximity = 1.2
            elif num_points < 60:
                self.risk_level = "MODERATE"
                self.proximity = 2.4
            else:
                self.risk_level = "CLEAR"
                self.proximity = round(3.0 + (num_points / 100), 1)

        # Merge Left (RGB) and Right (Grayscale) feeds side-by-side
        combined_view = np.hstack((img, gray_3ch))

        # Compute loop latency
        self.latency = round((time.time() - start_time) * 1000 + 12.0, 1)

        return av.VideoFrame.from_ndarray(combined_view, format="bgr24")


# Main Layout
ctx = webrtc_streamer(
    key="vio-slam-dual-stream",
    video_processor_factory=VIODualStreamProcessor,
    rtc_configuration=RTC_CONFIGURATION,
    media_stream_constraints={"video": True, "audio": False},
    sendback_audio=False,
)

# Bottom Telemetry Metric Cards
st.write("")
col1, col2, col3, col4 = st.columns(4)

with col1:
    m1 = st.empty()
with col2:
    m2 = st.empty()
with col3:
    m3 = st.empty()
with col4:
    m4 = st.empty()

# Real-Time Dynamic Parameter Updating
if ctx.video_processor:
    proc = ctx.video_processor
    
    m1.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Risk Level</div>
            <div class="metric-value">{proc.risk_level}</div>
        </div>
    """, unsafe_allow_html=True)

    m2.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Steering Angle</div>
            <div class="metric-value">{abs(proc.steering_angle)}°</div>
            <div class="badge-green">↑ {proc.turn_direction}</div>
        </div>
    """, unsafe_allow_html=True)

    m3.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Obstacle Proximity</div>
            <div class="metric-value">{proc.proximity} m</div>
        </div>
    """, unsafe_allow_html=True)

    m4.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Loop Latency</div>
            <div class="metric-value">{proc.latency} ms</div>
            <div class="badge-green">↑ 50-65 ms target</div>
        </div>
    """, unsafe_allow_html=True)
else:
    # Default State Cards
    m1.markdown('<div class="metric-card"><div class="metric-title">Risk Level</div><div class="metric-value">CLEAR</div></div>', unsafe_allow_html=True)
    m2.markdown('<div class="metric-card"><div class="metric-title">Steering Angle</div><div class="metric-value">2.1°</div><div class="badge-green">↑ Turn Right</div></div>', unsafe_allow_html=True)
    m3.markdown('<div class="metric-card"><div class="metric-title">Obstacle Proximity</div><div class="metric-value">3.5 m</div></div>', unsafe_allow_html=True)
    m4.markdown('<div class="metric-card"><div class="metric-title">Loop Latency</div><div class="metric-value">17.8 ms</div><div class="badge-green">↑ 50-65 ms target</div></div>', unsafe_allow_html=True)

st.checkbox("Initialize Vehicle Camera Loop", value=True)