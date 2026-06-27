import streamlit as st
import os
import pandas as pd
from detector import process_video

st.set_page_config(
    page_title="Inventory Removal Detection",
    page_icon="📦",
    layout="wide"
)
st.set_page_config(page_title="SuperTails",layout="wide", page_icon="https://i.ibb.co/spW9Jvr5/supertails.jpg",)
# Streamlit UI
st.markdown("""
        <style>
               .block-container {
                    padding-top: 2.2rem;
                    padding-left: 3.5rem;
                    padding-right: 3.5rem;
                }
        </style>
        """, unsafe_allow_html=True)

import streamlit as st

# Logo and Green Line
import streamlit as st

# 1. Create two columns with specific width ratios (adjust ratios as needed)
import streamlit as st

import streamlit as st

import streamlit as st

st.text("")
st.text("")

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
st.markdown(
"""
You can try using the following sample footages for testing the application:  [Sample Images on Google Drive](https://drive.google.com/drive/folders/1ukKwUSMEYPzks8GdULB5dXZP6ZLDXvMe?usp=sharing)
"""
)

if uploaded_file is not None:

    os.makedirs("input", exist_ok=True)

    input_path = os.path.join(
        "input",
        uploaded_file.name
    )

    with open(input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success("Video uploaded successfully!")

    if st.button("▶ Process Video"):

        with st.spinner("Processing video... Please wait."):

            output_video, events_csv = process_video(input_path)

        st.success("Processing Complete!")

        st.subheader("Processed Video")

        with open(output_video, "rb") as f:
            video_bytes = f.read()

        st.video(video_bytes)

        st.subheader("Detected Events")

        df = pd.read_csv(events_csv)

        st.dataframe(df, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:

            with open(events_csv, "rb") as file:

                st.download_button(
                    label="⬇ Download Event Log",
                    data=file,
                    file_name="events.csv",
                    mime="text/csv"
                )

        with col2:

            with open(output_video, "rb") as file:

                st.download_button(
                    label="⬇ Download Output Video",
                    data=file,
                    file_name="output.mp4",
                    mime="video/mp4"
                )