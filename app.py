import streamlit as st
import os
import pandas as pd
from moviepy.editor import VideoFileClip
from detector import process_video

# 1. Page Configuration
st.set_page_config(
    page_title="SuperTails - Inventory Removal Detection",
    layout="wide", 
    page_icon="https://i.ibb.co/spW9Jvr5/supertails.jpg"
)

# 2. Page Layout Styling
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

# 3. Branding & Header Section
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

# Green divider line
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

# 4. File Uploader
uploaded_file = st.file_uploader(
    "Upload CCTV Video",
    type=["mp4", "avi", "mov"]
)

st.markdown("""
<div class="sample-box">
    <strong>💡 Quick Testing Tip:</strong> You can try using the following sample footages for testing the application: 
    <a href="https://drive.google.com/drive/folders/1AiUoF8qRufmGj5l4KtQKzAONpwWiTkLp?usp=sharing" target="_blank" style="font-weight: bold; color: #0066cc; text-decoration: underline;">
        Sample footages on Google Drive
    </a>
</div>
""", unsafe_allow_html=True)

# 5. Initialize Streamlit Session State
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

    # --- Processing Trigger ---
    if st.button("▶ Process Video"):
        with st.spinner("Processing video... Please wait."):
            # 1. Run the original backend model logic
            raw_video, events_csv = process_video(input_path)
            
            # 2. Define path for browser-safe video file
            web_safe_video = raw_video.replace(".mp4", "_web.mp4")
            
            try:
                # 3. Force conversion to H.264 using pure Python library
                clip = VideoFileClip(raw_video)
                clip.write_videofile(web_safe_video, codec="libx264", audio=False, verbose=False, logger=None)
                clip.close()
                final_video = web_safe_video
            except Exception as e:
                # Fallback if conversion hits a file permissions error
                final_video = raw_video
            
            # Save final paths directly to state memory
            st.session_state.output_video = final_video
            st.session_state.events_csv = events_csv
            st.session_state.processed = True
            
        st.success("Processing Complete!")

    # 6. Render interface UI components from stable state memory
    if st.session_state.processed:
        st.subheader("Processed Video")

        # Read output video bytes
        with open(st.session_state.output_video, "rb") as f:
            video_bytes = f.read()

        # This will now natively load via the standard st.video player!
        st.video(video_bytes, format="video/mp4")

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
                    file_name="output.mp4",
                    mime="video/mp4"
                )