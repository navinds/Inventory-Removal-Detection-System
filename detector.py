import cv2
import pandas as pd
from ultralytics import YOLO
from skimage.metrics import structural_similarity as ssim
import os


def process_video(video_path):

    os.makedirs("output", exist_ok=True)

    output_video_path = "output/output.mp4"
    output_csv_path = "output/events.csv"

    model = YOLO("yolov8n.pt")

    ROI_X1, ROI_Y1 = 180, 0
    ROI_X2, ROI_Y2 = 1110, 280

    cap = cv2.VideoCapture(video_path)

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    out = cv2.VideoWriter(
        output_video_path,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height)
    )

    frame_number = 0

    interaction_active = False
    before_roi = None

    display_text = ""
    display_until = 0

    events = []

    while True:

        ret, frame = cap.read()
        if not ret:
            break

        frame_number += 1

        annotated = frame.copy()

        cv2.rectangle(annotated,(ROI_X1,ROI_Y1),(ROI_X2,ROI_Y2),(0,255,0),2)
        cv2.putText(annotated,"Shelf ROI",(ROI_X1+10,30),
                    cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,255,0),2)

        results = model(frame, verbose=False)

        person_inside = False

        for result in results:
            for box in result.boxes:

                if int(box.cls[0]) != 0:
                    continue

                conf=float(box.conf[0])
                if conf<0.5:
                    continue

                x1,y1,x2,y2=map(int,box.xyxy[0])

                cv2.rectangle(annotated,(x1,y1),(x2,y2),(255,0,0),2)
                cv2.putText(annotated,f"Person {conf:.2f}",(x1,y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,0,0),2)

                topx=(x1+x2)//2
                topy=y1

                if ROI_X1<=topx<=ROI_X2 and ROI_Y1<=topy<=ROI_Y2:
                    person_inside=True

        # interaction starts
        if person_inside and not interaction_active:
            interaction_active=True
            before_roi=frame[ROI_Y1:ROI_Y2,ROI_X1:ROI_X2].copy()

        # interaction ends
        elif interaction_active and not person_inside:

            interaction_active=False

            after_roi=frame[ROI_Y1:ROI_Y2,ROI_X1:ROI_X2].copy()

            gray_before=cv2.cvtColor(before_roi,cv2.COLOR_BGR2GRAY)
            gray_after=cv2.cvtColor(after_roi,cv2.COLOR_BGR2GRAY)

            score,_=ssim(gray_before,gray_after,full=True)

            timestamp=round(frame_number/fps,2)

            if score<0.97:
                event="ITEM_REMOVED"
                confidence=round(max(0.5,min(0.99,1-score+0.5)),2)
                display_text="ITEM REMOVED"
            else:
                event="SHELF_INTERACTION"
                confidence=1.0
                display_text="SHELF INTERACTION"

            events.append({
                "Frame_Number":frame_number,
                "Timestamp":timestamp,
                "Event_Type":event,
                "Confidence_Score":confidence
            })

            display_until=frame_number+fps*2

        if frame_number<=display_until:
            cv2.putText(annotated,display_text,(40,60),
                        cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),3)

        out.write(annotated)

    cap.release()
    out.release()

    pd.DataFrame(events).to_csv(output_csv_path,index=False)

    return output_video_path, output_csv_path
