"""
Used Car Price Estimator - Flask Web Application & REST API
Course: Machine Learning, KLH University (Bowrampet Campus)
Team: B Rishik, Rohan V, M Nityay | Guide: Dr. G. S. Raghavendra Sir
"""

import os
import json
import time
import joblib
import numpy as np
import pandas as pd
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
DATA_DIR = os.path.join(BASE_DIR, "data")
CURRENT_YEAR = 2026

# Load Model & Metadata
model_path = os.path.join(MODELS_DIR, "best_model.joblib")
metadata_path = os.path.join(MODELS_DIR, "model_metadata.json")
dataset_path = os.path.join(DATA_DIR, "used_cars.csv")

if not os.path.exists(model_path) or not os.path.exists(metadata_path):
    raise FileNotFoundError("Model or metadata not found. Please run train_model.py first.")

model_pipeline = joblib.load(model_path)
with open(metadata_path, "r") as f:
    metadata = json.load(f)

# Cache dataset for explorer
dataset_df = None
if os.path.exists(dataset_path):
    dataset_df = pd.read_csv(dataset_path).dropna().drop_duplicates()

# Reference model specs for autofill
MODEL_DEFAULTS = {
    # Maruti Suzuki
    ("Maruti Suzuki", "Swift"): {"engine_cc": 1197, "max_power_bhp": 88.5, "mileage_kmpl": 22.3, "seats": 5},
    ("Maruti Suzuki", "Baleno"): {"engine_cc": 1197, "max_power_bhp": 88.5, "mileage_kmpl": 22.3, "seats": 5},
    ("Maruti Suzuki", "Dzire"): {"engine_cc": 1197, "max_power_bhp": 88.5, "mileage_kmpl": 22.4, "seats": 5},
    ("Maruti Suzuki", "Brezza"): {"engine_cc": 1462, "max_power_bhp": 101.6, "mileage_kmpl": 17.3, "seats": 5},
    ("Maruti Suzuki", "Ertiga"): {"engine_cc": 1462, "max_power_bhp": 101.6, "mileage_kmpl": 19.0, "seats": 7},
    ("Maruti Suzuki", "Alto"): {"engine_cc": 998, "max_power_bhp": 65.7, "mileage_kmpl": 24.3, "seats": 5},
    ("Maruti Suzuki", "WagonR"): {"engine_cc": 1197, "max_power_bhp": 88.5, "mileage_kmpl": 23.5, "seats": 5},
    # Hyundai
    ("Hyundai", "i20"): {"engine_cc": 1197, "max_power_bhp": 86.8, "mileage_kmpl": 20.0, "seats": 5},
    ("Hyundai", "Creta"): {"engine_cc": 1497, "max_power_bhp": 113.4, "mileage_kmpl": 16.8, "seats": 5},
    ("Hyundai", "Verna"): {"engine_cc": 1497, "max_power_bhp": 113.4, "mileage_kmpl": 17.7, "seats": 5},
    ("Hyundai", "Venue"): {"engine_cc": 1197, "max_power_bhp": 81.8, "mileage_kmpl": 17.5, "seats": 5},
    ("Hyundai", "Grand i10 Nios"): {"engine_cc": 1197, "max_power_bhp": 81.8, "mileage_kmpl": 20.7, "seats": 5},
    ("Hyundai", "Tucson"): {"engine_cc": 1999, "max_power_bhp": 153.8, "mileage_kmpl": 12.9, "seats": 5},
    # Honda
    ("Honda", "City"): {"engine_cc": 1498, "max_power_bhp": 119.3, "mileage_kmpl": 17.8, "seats": 5},
    ("Honda", "Amaze"): {"engine_cc": 1199, "max_power_bhp": 88.5, "mileage_kmpl": 18.6, "seats": 5},
    ("Honda", "Civic"): {"engine_cc": 1799, "max_power_bhp": 139.0, "mileage_kmpl": 16.5, "seats": 5},
    ("Honda", "WR-V"): {"engine_cc": 1199, "max_power_bhp": 88.7, "mileage_kmpl": 16.5, "seats": 5},
    # Toyota
    ("Toyota", "Innova Crysta"): {"engine_cc": 2393, "max_power_bhp": 147.5, "mileage_kmpl": 15.1, "seats": 7},
    ("Toyota", "Fortuner"): {"engine_cc": 2755, "max_power_bhp": 201.1, "mileage_kmpl": 10.0, "seats": 7},
    ("Toyota", "Glanza"): {"engine_cc": 1197, "max_power_bhp": 88.5, "mileage_kmpl": 22.3, "seats": 5},
    ("Toyota", "Urban Cruiser"): {"engine_cc": 1462, "max_power_bhp": 103.2, "mileage_kmpl": 17.0, "seats": 5},
    ("Toyota", "Camry"): {"engine_cc": 2487, "max_power_bhp": 175.7, "mileage_kmpl": 19.1, "seats": 5},
    # Tata
    ("Tata", "Nexon"): {"engine_cc": 1199, "max_power_bhp": 118.2, "mileage_kmpl": 17.4, "seats": 5},
    ("Tata", "Harrier"): {"engine_cc": 1956, "max_power_bhp": 167.6, "mileage_kmpl": 16.3, "seats": 5},
    ("Tata", "Safari"): {"engine_cc": 1956, "max_power_bhp": 167.6, "mileage_kmpl": 16.1, "seats": 7},
    ("Tata", "Altroz"): {"engine_cc": 1199, "max_power_bhp": 84.8, "mileage_kmpl": 19.3, "seats": 5},
    ("Tata", "Tiago"): {"engine_cc": 1199, "max_power_bhp": 84.8, "mileage_kmpl": 20.0, "seats": 5},
    ("Tata", "Punch"): {"engine_cc": 1199, "max_power_bhp": 86.6, "mileage_kmpl": 18.8, "seats": 5},
    # Mahindra
    ("Mahindra", "Thar"): {"engine_cc": 1997, "max_power_bhp": 150.0, "mileage_kmpl": 15.2, "seats": 4},
    ("Mahindra", "Scorpio-N"): {"engine_cc": 2198, "max_power_bhp": 172.4, "mileage_kmpl": 14.0, "seats": 7},
    ("Mahindra", "XUV700"): {"engine_cc": 1997, "max_power_bhp": 197.1, "mileage_kmpl": 13.0, "seats": 7},
    ("Mahindra", "XUV300"): {"engine_cc": 1197, "max_power_bhp": 108.6, "mileage_kmpl": 17.0, "seats": 5},
    ("Mahindra", "Bolero"): {"engine_cc": 1493, "max_power_bhp": 74.9, "mileage_kmpl": 16.0, "seats": 7},
    # Kia
    ("Kia", "Seltos"): {"engine_cc": 1497, "max_power_bhp": 113.4, "mileage_kmpl": 16.5, "seats": 5},
    ("Kia", "Sonet"): {"engine_cc": 1197, "max_power_bhp": 81.8, "mileage_kmpl": 18.4, "seats": 5},
    ("Kia", "Carens"): {"engine_cc": 1497, "max_power_bhp": 113.4, "mileage_kmpl": 16.5, "seats": 7},
    # Volkswagen
    ("Volkswagen", "Polo"): {"engine_cc": 999, "max_power_bhp": 108.6, "mileage_kmpl": 18.2, "seats": 5},
    ("Volkswagen", "Vento"): {"engine_cc": 999, "max_power_bhp": 108.6, "mileage_kmpl": 17.6, "seats": 5},
    ("Volkswagen", "Taigun"): {"engine_cc": 999, "max_power_bhp": 113.9, "mileage_kmpl": 18.1, "seats": 5},
    ("Volkswagen", "Virtus"): {"engine_cc": 999, "max_power_bhp": 113.9, "mileage_kmpl": 19.4, "seats": 5},
    # BMW
    ("BMW", "3 Series"): {"engine_cc": 1998, "max_power_bhp": 254.7, "mileage_kmpl": 16.1, "seats": 5},
    ("BMW", "5 Series"): {"engine_cc": 1995, "max_power_bhp": 187.7, "mileage_kmpl": 17.4, "seats": 5},
    ("BMW", "X1"): {"engine_cc": 1995, "max_power_bhp": 147.5, "mileage_kmpl": 19.2, "seats": 5},
    ("BMW", "X5"): {"engine_cc": 2993, "max_power_bhp": 281.6, "mileage_kmpl": 13.3, "seats": 5},
    # Mercedes-Benz
    ("Mercedes-Benz", "C-Class"): {"engine_cc": 1993, "max_power_bhp": 201.1, "mileage_kmpl": 16.9, "seats": 5},
    ("Mercedes-Benz", "E-Class"): {"engine_cc": 1950, "max_power_bhp": 194.0, "mileage_kmpl": 15.0, "seats": 5},
    ("Mercedes-Benz", "GLA"): {"engine_cc": 1950, "max_power_bhp": 187.7, "mileage_kmpl": 17.9, "seats": 5}
}

SAMPLE_PRESETS = [
    {
        "name": "Hyundai Creta 2021 (Diesel AT)",
        "brand": "Hyundai",
        "model": "Creta",
        "year": 2021,
        "km_driven": 38000,
        "fuel_type": "Diesel",
        "transmission": "Automatic",
        "owner": "First Owner",
        "engine_cc": 1497,
        "max_power_bhp": 113.4,
        "mileage_kmpl": 16.8,
        "seats": 5
    },
    {
        "name": "Maruti Swift 2018 (Petrol MT)",
        "brand": "Maruti Suzuki",
        "model": "Swift",
        "year": 2018,
        "km_driven": 62000,
        "fuel_type": "Petrol",
        "transmission": "Manual",
        "owner": "First Owner",
        "engine_cc": 1197,
        "max_power_bhp": 88.5,
        "mileage_kmpl": 22.3,
        "seats": 5
    },
    {
        "name": "Honda City 2019 (Petrol CVT)",
        "brand": "Honda",
        "model": "City",
        "year": 2019,
        "km_driven": 45000,
        "fuel_type": "Petrol",
        "transmission": "Automatic",
        "owner": "First Owner",
        "engine_cc": 1498,
        "max_power_bhp": 119.3,
        "mileage_kmpl": 17.8,
        "seats": 5
    },
    {
        "name": "Toyota Fortuner 2020 (Diesel 4x4)",
        "brand": "Toyota",
        "model": "Fortuner",
        "year": 2020,
        "km_driven": 72000,
        "fuel_type": "Diesel",
        "transmission": "Automatic",
        "owner": "First Owner",
        "engine_cc": 2755,
        "max_power_bhp": 201.1,
        "mileage_kmpl": 10.0,
        "seats": 7
    },
    {
        "name": "BMW 3 Series 2019 (Luxury Sedan)",
        "brand": "BMW",
        "model": "3 Series",
        "year": 2019,
        "km_driven": 48000,
        "fuel_type": "Petrol",
        "transmission": "Automatic",
        "owner": "First Owner",
        "engine_cc": 1998,
        "max_power_bhp": 254.7,
        "mileage_kmpl": 16.1,
        "seats": 5
    }
]

@app.route("/")
def index():
    return render_template("index.html", metadata=metadata, presets=SAMPLE_PRESETS)

@app.route("/api/metadata", methods=["GET"])
def get_metadata():
    return jsonify({
        "status": "success",
        "data": metadata
    })

@app.route("/api/model-specs", methods=["GET"])
def get_model_specs():
    brand = request.args.get("brand")
    model = request.args.get("model")
    specs = MODEL_DEFAULTS.get((brand, model))
    if specs:
        return jsonify({"status": "success", "specs": specs})
    return jsonify({"status": "not_found", "specs": None})

@app.route("/api/sample-cars", methods=["GET"])
def get_sample_cars():
    return jsonify({"status": "success", "samples": SAMPLE_PRESETS})

@app.route("/api/predict", methods=["POST"])
def predict_price():
    t_start = time.time()
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"status": "error", "message": "No JSON payload provided"}), 400

        # Validate & parse input fields
        brand = str(data.get("brand", "Maruti Suzuki")).strip()
        model = str(data.get("model", "Swift")).strip()
        year = int(data.get("year", 2020))
        km_driven = float(data.get("km_driven", 45000))
        fuel_type = str(data.get("fuel_type", "Petrol")).strip()
        transmission = str(data.get("transmission", "Manual")).strip()
        owner = str(data.get("owner", "First Owner")).strip()

        # Specs with fallbacks
        defaults = MODEL_DEFAULTS.get((brand, model), {"engine_cc": 1197, "max_power_bhp": 85.0, "mileage_kmpl": 18.0, "seats": 5})
        engine_cc = float(data.get("engine_cc", defaults["engine_cc"]))
        max_power_bhp = float(data.get("max_power_bhp", defaults["max_power_bhp"]))
        mileage_kmpl = float(data.get("mileage_kmpl", defaults["mileage_kmpl"]))
        seats = int(data.get("seats", defaults["seats"]))

        # Feature engineering
        car_age = CURRENT_YEAR - year
        km_per_year = km_driven / max(car_age, 1)
        power_per_liter = max_power_bhp / (engine_cc / 1000.0)

        # Assemble DataFrame matching training feature columns
        input_df = pd.DataFrame([{
            "brand": brand,
            "model": model,
            "car_age": car_age,
            "km_driven": km_driven,
            "km_per_year": km_per_year,
            "fuel_type": fuel_type,
            "transmission": transmission,
            "owner": owner,
            "mileage_kmpl": mileage_kmpl,
            "engine_cc": engine_cc,
            "max_power_bhp": max_power_bhp,
            "power_per_liter": power_per_liter,
            "seats": seats
        }])

        # Predict using trained pipeline
        pred_lakhs = float(model_pipeline.predict(input_df)[0])
        pred_lakhs = max(0.5, round(pred_lakhs, 2))  # minimum realistic floor

        # Formatted currency outputs
        inr_val = int(pred_lakhs * 100000)
        formatted_inr = f"₹ {inr_val:,}"
        formatted_lakhs = f"₹ {pred_lakhs:.2f} Lakhs"

        # Fair valuation range (± 5%)
        lower_bound = round(pred_lakhs * 0.95, 2)
        upper_bound = round(pred_lakhs * 1.05, 2)
        range_str = f"₹ {lower_bound:.2f}L – ₹ {upper_bound:.2f}L"

        # Market Insights & Driver Analysis
        latency_ms = round((time.time() - t_start) * 1000, 2)

        # Depreciation estimation
        depreciation_pct = min(85, round(car_age * 8.5 + (km_driven / 10000) * 1.2, 1))

        return jsonify({
            "status": "success",
            "prediction": {
                "price_lakhs": pred_lakhs,
                "price_inr": inr_val,
                "formatted_lakhs": formatted_lakhs,
                "formatted_inr": formatted_inr,
                "valuation_range": {
                    "lower_lakhs": lower_bound,
                    "upper_lakhs": upper_bound,
                    "range_formatted": range_str
                },
                "latency_ms": latency_ms,
                "model_used": metadata.get("best_model_name", "Gradient Boosting"),
                "insights": {
                    "car_age_years": car_age,
                    "annual_mileage_km": round(km_per_year, 0),
                    "estimated_depreciation": f"{depreciation_pct}%",
                    "fuel_efficiency_rating": "High" if mileage_kmpl > 20 else ("Moderate" if mileage_kmpl > 15 else "Performance Oriented"),
                    "negotiation_tip": f"Recommended offer band: {lower_bound:.2f}L for instant purchase, up to {upper_bound:.2f}L for certified pre-owned condition."
                }
            }
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/api/dataset-preview", methods=["GET"])
def get_dataset_preview():
    if dataset_df is None or dataset_df.empty:
        return jsonify({"status": "empty", "rows": []})
    limit = int(request.args.get("limit", 15))
    sample_data = dataset_df.sample(min(limit, len(dataset_df)), random_state=42).to_dict(orient="records")
    return jsonify({
        "status": "success",
        "total_records": len(dataset_df),
        "rows": sample_data
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    print(f"\n🚗 Used Car Price Estimator Web App running on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
