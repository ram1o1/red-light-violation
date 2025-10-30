import cv2
import pandas as pd
import os
import config

os.makedirs(config.OUTPUT_PATH, exist_ok=True)

cap = cv2.VideoCapture(config.VIDEO_PATH)

frame_count = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame_count += 1
    if frame_count % 30 == 0:
        frame_name = os.path.join(config.OUTPUT_PATH, f"frame_{frame_count}.jpg")
        cv2.imwrite(frame_name, frame)

cap.release()
print("✅ Frames extracted successfully!")
