import mysql.connector
import pandas as pd
import os

# ---------- Configuration ----------
CSV_PATH = "outputs\license_plates.csv"  # updated path
DB_CONFIG = {
    "host": "localhost",
    "user": "root",           # change if needed
    "password": "ravikagroup",       # change if needed
    "database": "traffic_violation_db"  # make sure this DB exists
}

# ---------- Step 1: Check CSV existence ----------
if not os.path.exists(CSV_PATH):
    print(f"[ERROR] CSV file not found at: {CSV_PATH}")
    exit()

# ---------- Step 2: Read or Generate Data ----------
print("Going into TRY Block")
try:
    df = pd.read_csv(CSV_PATH)
    print("After read csv")
    # If file is empty, generate dummy data
    if df.empty or len(df) == 0:
        print("[WARN] CSV file is empty. Generating 10 sample records...")
        df = pd.DataFrame({
            "license_plate": [f"GJ05AB{i:04d}" for i in range(10)],
            "vehicle_type": ["Car", "Bike", "Truck", "Car", "Bus", "Car", "Auto", "Truck", "Bike", "Bus"],
            "time_of_violation": [
                "2025-10-30 09:00", "2025-10-30 09:15", "2025-10-30 09:30",
                "2025-10-30 09:45", "2025-10-30 10:00", "2025-10-30 10:15",
                "2025-10-30 10:30", "2025-10-30 10:45", "2025-10-30 11:00", "2025-10-30 11:15"
            ],
            "location": ["Vadodara Signal"] * 10,
            "fine_amount": [500, 300, 800, 400, 600, 500, 300, 700, 350, 650]
        })
        # overwrite CSV for future use
        df.to_csv(CSV_PATH, index=False)
except Exception as e:
    print(f"[ERROR] Failed to read or generate CSV: {e}")
    exit()

# ---------- Step 3: Connect to MySQL ----------
try:
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    print("[INFO] Connected to MySQL database successfully.")
except Exception as e:
    print(f"[ERROR] Database connection failed: {e}")
    exit()

# ---------- Step 4: Create Table ----------
create_table_query = """
CREATE TABLE IF NOT EXISTS redlight_violations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    license_plate VARCHAR(20),
    vehicle_type VARCHAR(50),
    time_of_violation VARCHAR(50),
    location VARCHAR(100),
    fine_amount FLOAT
)
"""
cursor.execute(create_table_query)
conn.commit()

# ---------- Step 5: Insert Data ----------
insert_query = """
INSERT INTO redlight_violations 
(license_plate, vehicle_type, time_of_violation, location, fine_amount)
VALUES (%s, %s, %s, %s, %s)
"""

try:
    for _, row in df.iterrows():
        cursor.execute(insert_query, (
            row['license_plate'],
            row['vehicle_type'],
            row['time_of_violation'],
            row['location'],
            row['fine_amount']
        ))
    conn.commit()
    print(f"[INFO] Inserted {len(df)} records into database successfully.")
except Exception as e:
    print(f"[ERROR] Failed to insert data: {e}")
    conn.rollback()

# ---------- Step 6: Close Connection ----------
cursor.close()
conn.close()
print("[INFO] Database connection closed.")
