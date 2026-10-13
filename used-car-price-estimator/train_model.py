"""
Model Training & Evaluation Pipeline for Used Car Price Estimator
Implements the full ML workflow specified in the course project PPT & Abstract:
1. Data Ingestion & Cleaning (Missing values, duplicates, outliers)
2. Feature Engineering (car_age, km_per_year, power_per_liter, encodings)
3. Model Training & Comparison:
   - Linear Regression
   - Random Forest Regressor
   - Gradient Boosting Regressor
4. Metric Evaluation (R², MAE, RMSE) & Feature Importance extraction
5. Model Persistence with Joblib and Metadata JSON export
"""

import os
import json
import time
import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import r2_score, mean_absolute_error, root_mean_squared_error
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

CURRENT_YEAR = 2026

def load_and_clean_data(csv_path):
    print("=" * 60)
    print("STEP 1: DATA INGESTION & CLEANING")
    print("=" * 60)
    df = pd.read_csv(csv_path)
    initial_rows = len(df)
    print(f"Loaded raw dataset with {initial_rows} records.")

    # 1. Remove duplicate records
    dup_count = df.duplicated().sum()
    df = df.drop_duplicates()
    print(f"Removed {dup_count} duplicate records. Remaining: {len(df)}")

    # 2. Impute missing values
    numeric_cols = ["km_driven", "mileage_kmpl", "engine_cc", "max_power_bhp", "seats"]
    for col in numeric_cols:
        if col in df.columns and df[col].isnull().sum() > 0:
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            print(f"Imputed missing values in '{col}' with median: {median_val:.2f}")

    # 3. Handle outliers (IQR filtering for selling price and km_driven)
    q1_km = df['km_driven'].quantile(0.01)
    q3_km = df['km_driven'].quantile(0.99)
    df = df[(df['km_driven'] >= q1_km) & (df['km_driven'] <= q3_km)]

    q1_price = df['selling_price'].quantile(0.01)
    q3_price = df['selling_price'].quantile(0.99)
    df = df[(df['selling_price'] >= q1_price) & (df['selling_price'] <= q3_price)]

    print(f"Cleaned dataset records: {len(df)} rows after outlier filtering.")
    return df

def engineer_features(df):
    print("=" * 60)
    print("STEP 2: FEATURE ENGINEERING")
    print("=" * 60)
    df = df.copy()

    # Derived Feature 1: Vehicle Age
    df['car_age'] = CURRENT_YEAR - df['year']

    # Derived Feature 2: Mileage per Year Ratio
    df['km_per_year'] = df['km_driven'] / np.maximum(df['car_age'], 1)

    # Derived Feature 3: Power to Engine Displacement Ratio
    df['power_per_liter'] = df['max_power_bhp'] / (df['engine_cc'] / 1000.0)

    print("Created derived features: 'car_age', 'km_per_year', 'power_per_liter'")
    return df

def train_and_evaluate_models(data_path, models_dir):
    os.makedirs(models_dir, exist_ok=True)
    df = load_and_clean_data(data_path)
    df = engineer_features(df)

    # Define target and features
    target_col = "selling_price"
    feature_cols = [
        "brand", "model", "car_age", "km_driven", "km_per_year",
        "fuel_type", "transmission", "owner",
        "mileage_kmpl", "engine_cc", "max_power_bhp", "power_per_liter", "seats"
    ]

    X = df[feature_cols]
    y = df[target_col]

    # Split train/test (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"Training set: {len(X_train)} samples | Test set: {len(X_test)} samples")

    categorical_features = ["brand", "model", "fuel_type", "transmission", "owner"]
    numeric_features = [
        "car_age", "km_driven", "km_per_year",
        "mileage_kmpl", "engine_cc", "max_power_bhp", "power_per_liter", "seats"
    ]

    # Preprocessing pipelines
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler())
            ]), numeric_features),
            ("cat", Pipeline([
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
            ]), categorical_features)
        ]
    )

    # Models specified in PPT
    candidate_models = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(
            n_estimators=150, max_depth=16, min_samples_split=4, random_state=42, n_jobs=-1
        ),
        "Gradient Boosting": GradientBoostingRegressor(
            n_estimators=180, learning_rate=0.08, max_depth=5, random_state=42
        )
    }

    print("=" * 60)
    print("STEP 3: MODEL TRAINING & BENCHMARK COMPARISON")
    print("=" * 60)

    results = {}
    best_name = None
    best_score = -float("inf")
    best_pipeline = None

    for name, model in candidate_models.items():
        t0 = time.time()
        pipeline = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("regressor", model)
        ])

        pipeline.fit(X_train, y_train)
        train_time = round(time.time() - t0, 3)

        # Predictions
        y_pred = pipeline.predict(X_test)

        r2 = float(r2_score(y_test, y_pred))
        mae = float(mean_absolute_error(y_test, y_pred))
        rmse = float(root_mean_squared_error(y_test, y_pred))

        results[name] = {
            "r2_score": round(r2, 4),
            "mae": round(mae, 4),
            "rmse": round(rmse, 4),
            "train_time_sec": train_time,
            "accuracy_pct": round(r2 * 100, 2)
        }

        print(f"[{name}]")
        print(f"  R² Score:  {r2:.4f} ({r2*100:.2f}%)")
        print(f"  MAE:       ₹{mae:.2f} Lakhs")
        print(f"  RMSE:      ₹{rmse:.2f} Lakhs")
        print(f"  Train Time: {train_time}s\n")

        if r2 > best_score:
            best_score = r2
            best_name = name
            best_pipeline = pipeline

    print(f"🏆 Best Model: {best_name} with R² = {best_score:.4f} ({best_score*100:.2f}%)")

    # Extract Feature Importance (from Random Forest or Gradient Boosting)
    rf_pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("regressor", candidate_models["Random Forest"])
    ])
    rf_pipeline.fit(X_train, y_train)
    rf_model = rf_pipeline.named_steps["regressor"]
    onehot_encoder = rf_pipeline.named_steps["preprocessor"].named_transformers_["cat"].named_steps["onehot"]
    cat_feature_names = list(onehot_encoder.get_feature_names_out(categorical_features))
    all_feature_names = numeric_features + cat_feature_names
    importances = rf_model.feature_importances_

    # Aggregate importance by original concept
    concept_importance = {
        "Car Age (Depreciation)": 0.0,
        "Kilometers Driven": 0.0,
        "Engine CC & Displacement": 0.0,
        "Max Power (BHP)": 0.0,
        "Power / Liter Ratio": 0.0,
        "Km / Year Ratio": 0.0,
        "Fuel Economy (Mileage)": 0.0,
        "Brand & Model Value": 0.0,
        "Transmission Type": 0.0,
        "Fuel Type": 0.0,
        "Owner History": 0.0,
        "Seating Capacity": 0.0
    }

    for fname, imp in zip(all_feature_names, importances):
        if fname == "car_age":
            concept_importance["Car Age (Depreciation)"] += imp
        elif fname == "km_driven":
            concept_importance["Kilometers Driven"] += imp
        elif fname == "engine_cc":
            concept_importance["Engine CC & Displacement"] += imp
        elif fname == "max_power_bhp":
            concept_importance["Max Power (BHP)"] += imp
        elif fname == "power_per_liter":
            concept_importance["Power / Liter Ratio"] += imp
        elif fname == "km_per_year":
            concept_importance["Km / Year Ratio"] += imp
        elif fname == "mileage_kmpl":
            concept_importance["Fuel Economy (Mileage)"] += imp
        elif fname == "seats":
            concept_importance["Seating Capacity"] += imp
        elif fname.startswith("brand_") or fname.startswith("model_"):
            concept_importance["Brand & Model Value"] += imp
        elif fname.startswith("transmission_"):
            concept_importance["Transmission Type"] += imp
        elif fname.startswith("fuel_type_"):
            concept_importance["Fuel Type"] += imp
        elif fname.startswith("owner_"):
            concept_importance["Owner History"] += imp

    # Sort importances descending
    sorted_concept_importance = [
        {"feature": k, "importance": round(float(v) * 100, 2)}
        for k, v in sorted(concept_importance.items(), key=lambda x: x[1], reverse=True)
    ]

    # Save best model pipeline
    best_model_path = os.path.join(models_dir, "best_model.joblib")
    joblib.dump(best_pipeline, best_model_path)
    print(f"Saved best model pipeline to {best_model_path}")

    # Unique dropdown values for UI
    brand_models_map = {}
    for brand in sorted(df["brand"].unique()):
        brand_models_map[brand] = sorted(df[df["brand"] == brand]["model"].unique().tolist())

    metadata = {
        "best_model_name": best_name,
        "target_accuracy": "85%+",
        "achieved_accuracy": f"{best_score * 100:.2f}%",
        "models_comparison": results,
        "feature_importances": sorted_concept_importance,
        "dataset_summary": {
            "total_records": int(len(df)),
            "train_records": int(len(X_train)),
            "test_records": int(len(X_test)),
            "price_min": round(float(df["selling_price"].min()), 2),
            "price_max": round(float(df["selling_price"].max()), 2),
            "price_median": round(float(df["selling_price"].median()), 2),
            "brands_count": int(df["brand"].nunique()),
            "models_count": int(df["model"].nunique())
        },
        "brand_models_map": brand_models_map,
        "fuel_types": sorted(df["fuel_type"].unique().tolist()),
        "transmissions": sorted(df["transmission"].unique().tolist()),
        "owners": ["First Owner", "Second Owner", "Third Owner", "Fourth & Above"],
        "project_info": {
            "title": "Used Car Price Estimator",
            "subtitle": "Predicting fair market value of pre-owned vehicles using regression-based machine learning",
            "team_members": [
                {"name": "B Rishik", "roll": "2520030314"},
                {"name": "Rohan V", "roll": "2520030558"},
                {"name": "M Nityay", "roll": "2520030618"}
            ],
            "guide": "Dr. G. S. Raghavendra Sir",
            "institution": "Koneru Lakshmaiah Education Foundation (KLH University – Bowrampet Campus)",
            "course": "Machine Learning"
        }
    }

    metadata_path = os.path.join(models_dir, "model_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved model metadata & metrics to {metadata_path}")

    return metadata

if __name__ == "__main__":
    data_file = "/Users/rohan/.gemini/antigravity/scratch/used-car-price-estimator/data/used_cars.csv"
    model_dir = "/Users/rohan/.gemini/antigravity/scratch/used-car-price-estimator/models"
    train_and_evaluate_models(data_file, model_dir)
