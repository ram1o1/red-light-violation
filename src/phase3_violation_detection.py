import cv2
import pandas as pd
import os
from collections import defaultdict
import config

# Parameters
input_folder = os.path.join(config.OUTPUT_PATH, "detections")
csv_path = os.path.join(input_folder, "vehicle_detections.csv")
output_video_path = os.path.join(config.OUTPUT_PATH, "redlight_violation_output.mp4")

# Virtual red light line (Y-coordinate)
RED_LINE_Y = 300  # adjust based on your frame height

# Load detection CSV
df = pd.read_csv(csv_path)

# Simple ID tracking (group detections by frame)
frame_detections = defaultdict(list)
for _, row in df.iterrows():
    frame_detections[row['frame']].append(row['label'])

# Load frames
frame_files = sorted([f for f in os.listdir(input_folder) if f.endswith(".jpg")])

if not frame_files:
    print("❌ No frames found for violation detection.")
    exit()

# Get frame size
sample_frame = cv2.imread(os.path.join(input_folder, frame_files[0]))
h, w, _ = sample_frame.shape

# Video writer
out = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), 10, (w, h))

# Placeholder for vehicle positions (simulate tracking)
vehicle_positions = defaultdict(int)

violations = []

for frame_file in frame_files:
    frame_path = os.path.join(input_folder, frame_file)
    frame = cv2.imread(frame_path)

    # Draw the red line
    cv2.line(frame, (0, RED_LINE_Y), (w, RED_LINE_Y), (0, 0, 255), 3)
    frame_name = os.path.splitext(frame_file)[0]

    # Simulate vehicle movement (for demo)
    for i, label in enumerate(frame_detections[frame_file]):
        y_pos = 100 + i * 50 + (int(frame_name.split('_')[-1]) % 50)  # mock motion
        vehicle_positions[label] = y_pos

        # Draw vehicle box placeholder
        color = (0, 255, 0)
        cv2.rectangle(frame, (100, y_pos - 20), (200, y_pos + 20), color, 2)
        cv2.putText(frame, label, (100, y_pos - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        # Check red line violation
        if y_pos > RED_LINE_Y:
            violations.append((frame_file, label))
            cv2.putText(frame, "🚨 VIOLATION", (220, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    
    out.write(frame)

out.release()

# Save violations CSV
violations_df = pd.DataFrame(violations, columns=["frame", "vehicle_type"])
violations_csv_path = os.path.join(config.OUTPUT_PATH, "redlight_violations.csv")
violations_df.to_csv(violations_csv_path, index=False)

print(f"✅ Red light violation detection complete!")
print(f"🚦 Violations saved to: {violations_csv_path}")
print(f"🎥 Video saved to: {output_video_path}")
