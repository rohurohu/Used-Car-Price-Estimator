# Used Car Price Estimator 🚗💰
### Predicting Fair Market Value of Pre-Owned Vehicles Using Regression-Based Machine Learning

**Academic Project** for Machine Learning Course  
**Institution**: Koneru Lakshmaiah Education Foundation (KLH University – Bowrampet Campus)  
**Under the Guidance of**: Dr. G. S. Raghavendra Sir  

**Submitted by**:
- **B Rishik** — 2520030314
- **Rohan V** — 2520030558
- **M Nityay** — 2520030618

---

## 📌 Project Overview
The used car market suffers from inconsistent and often subjective pricing, leaving buyers and sellers unsure of a vehicle's fair value. Sellers overprice and buyers underbid due to the lack of an objective, data-driven reference price.

This project implements an end-to-end Machine Learning system that accurately estimates the fair market resale value of pre-owned cars based on vehicle attributes, usage history, engine specifications, and brand equity.

The system incorporates:
1. **Data Ingestion & Cleaning**: Outlier removal, duplicate handling, and missing-value imputation.
2. **Feature Engineering**: Derived metrics including `car_age`, `km_per_year` intensity, and `power_per_liter`.
3. **Multi-Model Benchmarking**: Trains and compares Linear Regression, Random Forest, and Gradient Boosting regressors.
4. **Sub-second REST API**: Predicts prices in under 15ms (< 1s target).
5. **Interactive Web Dashboard**: Modern UI with 1-click test presets, negotiation bands, model accuracy charts, and live API tester.

---

## 🏆 Key Results & Performance
| Model | R² Score (%) | MAE (₹ Lakhs) | RMSE (₹ Lakhs) | Training Time |
| :--- | :---: | :---: | :---: | :---: |
| **Linear Regression** | 75.35% | ₹ 1.36L | ₹ 2.24L | ~0.03s |
| **Random Forest Regressor** | 96.15% | ₹ 0.49L | ₹ 0.89L | ~0.15s |
| **Gradient Boosting (Best)** 🏆 | **98.02%** | **₹ 0.37L** | **₹ 0.64L** | ~0.95s |

- **Target Accuracy**: 85%+ (Surpassed: **98.02%**)
- **Inference Latency**: < 15ms (Surpassed: < 1s target)
- **Error Margin**: ± ₹ 37,000 on average

---

## 🏗️ Project Architecture & Directory Structure
```
used-car-price-estimator/
├── app.py                     # Flask web server & REST API endpoints
├── generate_dataset.py        # Dataset generator (3,800+ realistic listings)
├── train_model.py             # Preprocessing pipeline, model training & export
├── requirements.txt           # Project dependencies
├── README.md                  # Detailed documentation & presentation notes
├── data/
│   └── used_cars.csv          # Cleaned dataset with 3,686 records
├── models/
│   ├── best_model.joblib      # Serialized Scikit-learn Pipeline (Gradient Boosting)
│   └── model_metadata.json    # Model evaluation metrics & feature importances
├── templates/
│   └── index.html             # Responsive web application UI
└── static/
    ├── css/
    │   └── style.css          # Glassmorphism, dark/light theme, modern UI
    └── js/
        └── app.js             # Client interactivity, Chart.js visuals, API console
```

---

## 🚀 How to Run the Website Locally

### 1. Prerequisites
Ensure you have Python 3.10+ installed.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Generate Dataset & Train Models (Already Pre-trained!)
If you ever want to re-run the dataset generation and model training:
```bash
python3 generate_dataset.py
python3 train_model.py
```

### 4. Start the Web Application
```bash
python3 app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5001
```

---

## 🔌 REST API Endpoints

### 1. Predict Car Price
- **URL**: `/api/predict`
- **Method**: `POST`
- **Content-Type**: `application/json`

**Sample Request**:
```json
{
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
}
```

**Sample Response**:
```json
{
  "status": "success",
  "prediction": {
    "price_lakhs": 10.42,
    "price_inr": 1042000,
    "formatted_lakhs": "₹ 10.42 Lakhs",
    "formatted_inr": "₹ 10,42,000",
    "valuation_range": {
      "lower_lakhs": 9.9,
      "upper_lakhs": 10.94,
      "range_formatted": "₹ 9.90L – ₹ 10.94L"
    },
    "latency_ms": 11.2,
    "model_used": "Gradient Boosting",
    "insights": {
      "car_age_years": 5,
      "annual_mileage_km": 7600,
      "estimated_depreciation": "34.0%",
      "fuel_efficiency_rating": "Moderate",
      "negotiation_tip": "Recommended offer band: 9.90L for direct individual transfer, up to 10.94L for certified pre-owned condition."
    }
  }
}
```

### 2. Model Metadata & Evaluation Metrics
- **URL**: `/api/metadata`
- **Method**: `GET`
- Returns model comparison tables, R² scores, MAE, RMSE, and feature importance rankings.

### 3. Dataset Preview
- **URL**: `/api/dataset-preview?limit=15`
- **Method**: `GET`
- Returns paginated random samples from the training dataset.

---

## 📊 Features & UI Capabilities
1. **Interactive Form with Auto-fill**: Select Brand & Model, and default engine CC, power, mileage, and seats auto-fill automatically.
2. **1-Click Test Presets**: Test with pre-configured popular cars (Creta Diesel, Swift Petrol, Honda City CVT, Fortuner 4x4, BMW 3 Series) with a single click.
3. **Fair Negotiation Band**: Shows lower and upper fair price bands for balanced buyer-seller negotiations.
4. **Model Comparison Visualizer**: Chart.js charts comparing Linear Regression, Random Forest, and Gradient Boosting.
5. **Feature Importance Explainability**: Highlights key drivers of vehicle depreciation (Age: 45.9%, Engine CC: 25.7%, Max Power: 15.8%).
6. **Live API Tester Console**: Test the REST API directly in the browser with customizable JSON requests.
7. **Theme Toggle**: Seamless switching between Dark Mode and Light Mode.
