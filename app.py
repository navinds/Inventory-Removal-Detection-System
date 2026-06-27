import streamlit as st
import os
import pandas as pd
import subprocess  # Required to fix the browser video playback issue
from detector import process_video

# 1. Set Page Configuration
st.set_page_config(
    page_title="SuperTails - Inventory Removal Detection",
    layout="wide", 
    page_icon="https://i.ibb.co/spW9Jvr5/supertails.jpg"
)

# 2. Page Styling
st.markdown("""
        <style>
               .block-container {
                    padding-top: 2.2rem;
                    padding-left: 3.5rem;
                    padding-right: 3.5rem;
                }
        </style>
        """, unsafe_allow_html=True)

st.text("")
st.text("")

# 3. Branding Header
left, center, right = st.columns([1, 2, 1])

with left:
    st.markdown("""
    <div style="height:140px; display:flex; align-items:center;">
        <img src="https://i.postimg.cc/vZrpVVdH/supertails-logo.png"
             style="width:250px; height:auto;">
    </div>
    """, unsafe_allow_html=True)

with center:
    st.markdown("""
    <div style="height:140px; display:flex; justify-content:center; align-items:center;">
        <img src="https://i.postimg.cc/RZF5t0XJ/Red-Modern-Welcome-Banner-Horizontal.png"
             style="width:400px; height:auto;">
    </div>
    """, unsafe_allow_html=True)

with right:
    st.empty()

# Green divider
st.markdown("""
    <hr style="
        border:none;
        height:3px;
        background:#BAE14A;
        width:100%;
        margin-top:15px;
        margin-bottom:25px;
    ">
""", unsafe_allow_html=True)

st.markdown("""
Upload a CCTV video to detect shelf interactions and item removal events.
""")

uploaded_file = st.file_uploader(
    "Upload CCTV Video",
    type=["mp4", "avi", "mov"]
)

st.markdown("""
You can try using the following sample footages for testing the application:  [Sample Images on Google Drive](https://drive.google.com/drive/folders/1ukKwUSMEYPzks8GdULB5dXZP6ZLDXvMe?usp=sharing)
""")

# --- INITIALIZE SESSION STATE ---
if 'processed' not in st.session_state:
    st.session_state.processed = False
    st.session_state.output_video = None
    st.session_state.events_csv = None

if uploaded_file is not None:
    os.makedirs("input", exist_ok=True)
    input_path = os.path.join("input", uploaded_file.name)

    with open(input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success("Video uploaded successfully!")

    # --- VIDEO PROCESSING & COVERTING BUTTON ---
    if st.button("▶ Process Video"):
        with st.spinner("Processing video... Please wait."):
            # Run your tracking model script
            output_video, events_csv = process_video(input_path)
            
            # Create a path for a browser-safe, playable MP4 version
            h264_output_path = output_video.replace(".mp4", "_playable.mp4")
            
            # Convert OpenCV's raw MP4 into a web-playable H.264 MP4 using FFmpeg
            try:
                subprocess.run([
                    'ffmpeg', '-y', '-i', output_video, 
                    '-vcodec', 'libx264', '-f', 'mp4', h264_output_path
                ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                final_video_path = h264_output_path
            except Exception as e:
                # If FFmpeg is missing on the machine, fallback to original output
                st.warning("FFmpeg conversion failed. Displaying uncompressed video.")
                final_video_path = output_video
            
            # Save final paths to session state memory
            st.session_state.output_video = final_video_path
            st.session_state.events_csv = events_csv
            st.session_state.processed = True
            
        st.success("Processing Complete!")

    # --- RENDER STABLE INTERFACE FROM MEMORY ---
    if st.session_state.processed:
        st.subheader("Processed Video")

        # Read the browser-safe video file 
        with open(st.session_state.output_video, "rb") as f:
            video_bytes = f.read()

        # This will now stream correctly in Chrome/Safari/Edge!
        st.video(video_bytes)

        st.subheader("Detected Events")

        df = pd.read_csv(st.session_state.events_csv)
        st.dataframe(df, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            with open(st.session_state.events_csv, "rb") as file:
                st.download_button(
                    label="⬇ Download Event Log",
                    data=file,
                    file_name="events.csv",
                    mime="text/csv"
                )

        with col2:
            with open(st.session_state.output_video, "rb") as file:
                st.download_button(
                    label="⬇ Download Output Video",
                    data=file,
                    file_name="output.mp4", # Will save as clean, playable MP4
                    mime="video/mp4"
                )