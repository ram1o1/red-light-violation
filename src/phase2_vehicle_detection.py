from ultralytics import YOLO
import os
import cv2
import pandas as pd
from tqdm import tqdm
import config

# Load pretrained YOLOv8 model
model = YOLO("yolov8n.pt")  # lightweight model (downloads automatically)

# Paths
input_folder = config.OUTPUT_PATH
output_folder = os.path.join(config.OUTPUT_PATH, "detections")
os.makedirs(output_folder, exist_ok=True)

data = []

# Run detection on each frame
for frame_file in tqdm(sorted(os.listdir(input_folder))):
    if frame_file.endswith(".jpg"):
        frame_path = os.path.join(input_folder, frame_file)
        results = model(frame_path, verbose=False)

        # Get detections
        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                label = model.names[cls]

                # Save detection info
                data.append({
                    "frame": frame_file,
                    "label": label,
                    "confidence": conf
                })

        # Save annotated image
        annotated_frame = results[0].plot()
        cv2.imwrite(os.path.join(output_folder, frame_file), annotated_frame)

# Save detections to CSV
df = pd.DataFrame(data)
csv_path = os.path.join(output_folder, "vehicle_detections.csv")
df.to_csv(csv_path, index=False)

print(f"✅ Detection completed! Results saved to: {csv_path}")
