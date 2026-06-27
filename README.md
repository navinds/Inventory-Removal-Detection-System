# 📦 SuperShelf – Inventory Removal Detection System

## Live Demo

**Streamlit App:** https://navinssupershelf.streamlit.app/

---

# Problem Statement

Retail stores often rely on CCTV cameras to monitor shelves. However, manually reviewing footage to determine whether a customer actually removed a product is time-consuming and inefficient.

The objective of this project is to automatically detect shelf interactions and identify whether an item has been removed from a predefined shelf region.

The system should generate a structured event log containing:

* Timestamp / Frame Number
* Event Type (`ITEM_REMOVED` or `SHELF_INTERACTION`)
* Confidence Score

---

# Architecture Overview

```
Input CCTV Video
        │
        ▼
Person Detection (YOLOv8)
        │
        ▼
Shelf ROI Monitoring
        │
        ▼
Detect Person Entering ROI
        │
        ▼
Capture Shelf Image (Before Interaction)
        │
        ▼
Person Leaves ROI
        │
        ▼
Capture Shelf Image (After Interaction)
        │
        ▼
SSIM Comparison (Compare shelf images before and after interaction)
        │
        ▼
Decision Logic
        │
        ▼
Output Video + CSV Event Log
```

---

# Technologies Used

| Technology                         | Purpose                                           |
| ---------------------------------- | ------------------------------------------------- |
| Python                             | Core application                                  |
| OpenCV                             | Video processing and frame extraction             |
| YOLOv8 Nano                        | Person detection                                  |
| SSIM (Structural Similarity Index) | Compare shelf images before and after interaction |
| Pandas                             | Generate CSV event log                            |
| Streamlit                          | Interactive web application                       |

---

# Why These Technologies?

## 1. YOLOv8 Nano

YOLOv8 Nano is a lightweight real-time object detection model.

It is used to detect whether a person is interacting with the shelf.

**Why YOLO?**

* Fast inference
* Good person detection accuracy
* Lightweight enough for real-time applications
* Easy integration with Python

---

## 2. ROI (Region of Interest)

Instead of analyzing the entire frame, the system only monitors the predefined shelf region.

This significantly reduces unnecessary computations and prevents unrelated movements elsewhere in the video from triggering detections.

---

## 3. SSIM (Structural Similarity Index)

SSIM compares the shelf image before and after customer interaction.

Instead of comparing raw pixel values, SSIM evaluates structural similarity between images.

If the similarity drops below a predefined threshold, the system considers that a visual change has occurred on the shelf.

---

# Why Not Optical Flow?

Optical Flow measures motion between consecutive frames.

Although it detects movement very well, it cannot determine whether an item was actually removed.

It mainly captures motion while the customer is interacting with the shelf.

Since the objective is to compare the shelf before and after interaction, SSIM is more suitable.

---

# Why Not Object Detection for Products?

A product detection model would require:

* Product annotations
* Large labelled dataset
* Model training

Since no labelled product dataset was provided, detecting the visual change on the shelf using SSIM is a simpler and more practical solution.

---

# Why Not Pose Estimation?

Pose estimation detects body joints and hand movements.

While it can indicate that a customer reached toward the shelf, it cannot confirm whether a product was actually removed.

Therefore, person detection combined with image comparison provides a simpler and more reliable pipeline for this problem.

---

# How the System Works

### Step 1

The user uploads a CCTV video through the Streamlit application.

---

### Step 2

YOLOv8 detects people in every frame.

---

### Step 3

When a detected person enters the predefined shelf ROI, the system stores the current shelf image.

This acts as the reference image before interaction.

---

### Step 4

When the person leaves the ROI, another shelf image is captured.

This becomes the after-interaction image.

---

## Step 5

The system compares the shelf images captured before and after the interaction using SSIM (Structural Similarity Index).

* If the similarity is below the predefined threshold, the event is classified as **ITEM_REMOVED**.
* Otherwise, the event is classified as **SHELF_INTERACTION**.

**Note:** A customer interaction may generate one or more `SHELF_INTERACTION` events before an `ITEM_REMOVED` event is detected. This is expected behavior. The system first detects interaction with the shelf and then evaluates whether a permanent visual change has occurred after the interaction. If no significant change is observed, the event is logged as `SHELF_INTERACTION`. If a subsequent interaction results in a product being removed, the corresponding event is logged as `ITEM_REMOVED`.


---
### Step 6

The system generates:

* Processed output video
* CSV event log

---

# Event Detection Logic

```text
Person enters Shelf ROI
        │
Capture Before Image
        │
Customer interacts with shelf
        │
Person leaves Shelf ROI
        │
Capture After Image
        │
Compare Before & After using SSIM
        │
        ├── Significant visual change detected
        │          │
        │          └── ITEM_REMOVED
        │
        └── No significant visual change
                   │
                   └── SHELF_INTERACTION
```

---

# Confidence Score

The project specification requires every detected event to include a `Confidence_Score`.

Since this solution is based on a rule-based computer vision pipeline rather than a machine learning classifier, the system does not naturally produce a prediction probability.

Instead, the confidence score represents how confident the system is in the detected event based on the visual evidence observed after customer interaction.

For this implementation, the confidence score is derived from the image comparison performed using SSIM. A larger visual difference between the shelf images generally results in a higher confidence for an `ITEM_REMOVED` event, while little or no visual difference indicates a `SHELF_INTERACTION` event.

The confidence score should therefore be interpreted as the system's certainty about the detected event rather than as a neural network prediction probability.


---

# Output

The application generates:

### 1. Annotated Video

* Shelf ROI
* Person detection
* Event labels

---

### 2. CSV Event Log

The system generates a structured CSV file containing the detected events from the uploaded video.

| Frame_Number | Timestamp | Event_Type        | Confidence_Score |
| -----------: | --------: | ----------------- | ---------------: |
|          245 |      8.17 | ITEM_REMOVED      |             0.92 |
|          528 |     17.60 | SHELF_INTERACTION |             0.90 |

**Column Description**

* **Frame_Number** – The frame number in the uploaded video where the event was detected.
* **Timestamp** – Time (in seconds) corresponding to the detected frame.
* **Event_Type** – Indicates whether an item was removed (`ITEM_REMOVED`) or the customer only interacted with the shelf (`SHELF_INTERACTION`).
* **Confidence_Score** – The estimated confidence of the detected event based on the visual evidence observed after customer interaction.

---

# Project Structure

```text
inventory-removal-detector/
│
├── .streamlit/
│   └── config.toml               # Streamlit configuration
│
├── app.py                        # Streamlit web application
├── detector.py                   # Core inventory removal detection pipeline
├── requirements.txt              # Python dependencies
├── README.md                     # Project documentation
```

---

# Future Improvements

* Product-level object detection
* Multi-person tracking
* Person re-identification
* Automatic shelf ROI detection
* Improved confidence estimation
* Real-time CCTV streaming support

---

# Conclusion

This project demonstrates a lightweight computer vision pipeline for detecting inventory removal from retail shelves using person detection, region-of-interest monitoring, and structural image comparison.

The solution is computationally efficient, easy to deploy, and suitable for prototype retail inventory monitoring applications.
