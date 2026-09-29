import streamlit as st
import cv2
import av
from streamlit_webrtc import webrtc_streamer, RTCConfiguration

RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

st.title("VIO-SLAM Vehicle Risk & Navigation Dashboard")

def video_frame_callback(frame: av.VideoFrame) -> av.VideoFrame:
    # 1. Convert PyAV VideoFrame to NumPy BGR array for OpenCV
    img = frame.to_ndarray(format="bgr24")

    # 2. Add your DynaFusion-VIO dynamic feature masking / live analysis here
    # Example: Draw live tracking metrics / dynamic mask directly onto 'img'
    cv2.putText(
        img, 
        "VIO-SLAM: ACTIVE (LIVE ANALYSIS)", 
        (20, 50), 
        cv2.FONT_HERSHEY_SIMPLEX, 
        0.8, 
        (0, 255, 0), 
        2
    )

    # 3. Return the processed OpenCV frame back as an av.VideoFrame to render live
    return av.VideoFrame.from_ndarray(img, format="bgr24")

webrtc_streamer(
    key="vio-slam-stream",
    video_frame_callback=video_frame_callback,
    rtc_configuration=RTC_CONFIGURATION,
    media_stream_constraints={"video": True, "audio": False},
)