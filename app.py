from flask import Flask, render_template
import mysql.connector
import pandas as pd

app = Flask(__name__)

# MySQL Connection Info — edit if needed
DB_CONFIG = {
    "host": "localhost",
    "user": "root",         # change if needed
    "password": "ravikagroup",     # change if needed
    "database": "traffic_violation_db"
}


def fetch_data():
    """Fetch all records from redlight_violations table"""
    conn = mysql.connector.connect(**DB_CONFIG)
    query = "SELECT * FROM redlight_violations"
    df = pd.read_sql(query, conn)
    conn.close()
    return df


@app.route('/')
def dashboard():
    """Main dashboard route"""
    df = fetch_data()
    total = len(df)
    total_fine = df['fine_amount'].sum() if not df.empty else 0
    per_vehicle = df['vehicle_type'].value_counts().to_dict() if not df.empty else {}
    return render_template(
        'index.html',
        records=df.to_dict(orient='records'),
        total=total,
        total_fine=total_fine,
        per_vehicle=per_vehicle
    )


if __name__ == '__main__':
    app.run(debug=True)
