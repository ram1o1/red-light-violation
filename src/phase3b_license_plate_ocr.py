"""
Phase 3B: License Plate OCR Recognition
---------------------------------------
This script scans vehicle images (from violation detection),
detects license plate regions, and extracts the alphanumeric text
using EasyOCR. The extracted results are stored in a CSV file for
database integration in the next phase.
"""

import os
import cv2
import pandas as pd
import easyocr
from datetime import datetime

# -------------------------------
# Paths
# -------------------------------
VIOLATION_DIR = "outputs/violations"
OUTPUT_CSV = "outputs/license_plates.csv"

# Create output folder if not present
os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

# -------------------------------
# Initialize OCR Reader
# -------------------------------
print("[INFO] Initializing EasyOCR...")
reader = easyocr.Reader(['en'], gpu=False)

# -------------------------------
# Helper Function
# -------------------------------
def extract_license_plate_text(image_path):
    """
    Reads an image and tries to extract license plate text using EasyOCR.
    Returns recognized text or None.
    """
    img = cv2.imread(image_path)
    if img is None:
        return None

    # Optionally resize for better OCR accuracy
    img = cv2.resize(img, (640, 480))

    # Perform OCR
    results = reader.readtext(img)

    # Collect text results
    detected_text = []
    for (bbox, text, prob) in results:
        if prob > 0.4 and 4 <= len(text) <= 12:  # Basic sanity check
            detected_text.append(text.strip())

    if detected_text:
        return " ".join(detected_text)
    return None


# -------------------------------
# Main Processing
# -------------------------------
def main():
    print("[INFO] Starting License Plate Recognition Phase...")

    data_records = []

    # Loop through violation images
    for file in os.listdir(VIOLATION_DIR):
        if file.lower().endswith((".jpg", ".png", ".jpeg")):
            image_path = os.path.join(VIOLATION_DIR, file)
            license_text = extract_license_plate_text(image_path)

            data_records.append({
                "image_file": file,
                "license_plate": license_text if license_text else "Not detected",
                "processed_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            print(f"[INFO] Processed {file} → {license_text}")

    # Convert to DataFrame
    df = pd.DataFrame(data_records)
    df.to_csv(OUTPUT_CSV, index=False)

    print(f"\n✅ License Plate OCR complete!")
    print(f"📄 Results saved at: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
