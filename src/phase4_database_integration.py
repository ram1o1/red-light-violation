import sqlite3
import pandas as pd
import os
import config

# File paths
violations_csv = os.path.join(config.OUTPUT_PATH, "redlight_violations.csv")
db_path = os.path.join(config.OUTPUT_PATH, "traffic_system.db")

# Connect to (or create) database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# -------------------- TABLE SETUP --------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS violations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    frame TEXT,
    vehicle_type TEXT,
    license_plate TEXT,
    fine_amount INTEGER,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS driver_profiles (
    license_plate TEXT PRIMARY KEY,
    driver_name TEXT,
    total_offenses INTEGER DEFAULT 0,
    license_points_deducted INTEGER DEFAULT 0,
    insurance_flag TEXT DEFAULT 'No'
)
""")

conn.commit()

# -------------------- INSERT NEW VIOLATIONS --------------------
if not os.path.exists(violations_csv):
    print("❌ No redlight_violations.csv found. Run Phase 3 first.")
    exit()

violations_df = pd.read_csv(violations_csv)

# Mock: assign fake license plates
violations_df["license_plate"] = [
    f"GJ01AB{i:03d}" for i in range(len(violations_df))
]

def calculate_fine(offense_count):
    if offense_count == 1:
        return 1000, 0, "No"
    elif offense_count == 2:
        return 2000, 1, "No"
    else:
        return 5000, 2, "Yes"

for _, row in violations_df.iterrows():
    lp = row["license_plate"]

    # Check existing driver
    cursor.execute("SELECT total_offenses FROM driver_profiles WHERE license_plate=?", (lp,))
    result = cursor.fetchone()

    if result:
        offense_count = result[0] + 1
        fine_amount, license_points, insurance_flag = calculate_fine(offense_count)
        cursor.execute("""
            UPDATE driver_profiles
            SET total_offenses=?, license_points_deducted=?, insurance_flag=?
            WHERE license_plate=?
        """, (offense_count, license_points, insurance_flag, lp))
    else:
        offense_count = 1
        fine_amount, license_points, insurance_flag = calculate_fine(offense_count)
        cursor.execute("""
            INSERT INTO driver_profiles (license_plate, driver_name, total_offenses, license_points_deducted, insurance_flag)
            VALUES (?, ?, ?, ?, ?)
        """, (lp, f"Driver_{lp[-3:]}", offense_count, license_points, insurance_flag))

    # Record violation
    cursor.execute("""
        INSERT INTO violations (frame, vehicle_type, license_plate, fine_amount)
        VALUES (?, ?, ?, ?)
    """, (row["frame"], row["vehicle_type"], lp, fine_amount))

conn.commit()
print(f"✅ Database updated successfully at {db_path}")

# -------------------- DISPLAY SUMMARY --------------------
print("\n📋 Driver Profiles Summary:")
profiles = pd.read_sql_query("SELECT * FROM driver_profiles", conn)
print(profiles)

print("\n📋 Violations Summary:")
violations = pd.read_sql_query("SELECT * FROM violations", conn)
print(violations.head())

conn.close()
