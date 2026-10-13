"""
Dataset Generator & Preprocessor for Used Car Price Estimator
Generates a realistic historical dataset of pre-owned vehicles in India,
simulating real marketplace distributions (Cardekho / Cars24 / OLX style).
"""

import numpy as np
import pandas as pd
import os

def generate_used_car_data(n_samples=3500, random_state=42):
    np.random.seed(random_state)

    brand_models = {
        "Maruti Suzuki": [
            ("Swift", 7.5, 1197, 88.5, 22.3, "Hatchback", 5),
            ("Baleno", 8.2, 1197, 88.5, 22.3, "Hatchback", 5),
            ("Dzire", 8.0, 1197, 88.5, 22.4, "Sedan", 5),
            ("Brezza", 10.5, 1462, 101.6, 17.3, "SUV", 5),
            ("Ertiga", 11.2, 1462, 101.6, 19.0, "MUV", 7),
            ("Alto", 4.5, 998, 65.7, 24.3, "Hatchback", 5),
            ("WagonR", 6.0, 1197, 88.5, 23.5, "Hatchback", 5)
        ],
        "Hyundai": [
            ("i20", 8.8, 1197, 86.8, 20.0, "Hatchback", 5),
            ("Creta", 14.5, 1497, 113.4, 16.8, "SUV", 5),
            ("Verna", 13.0, 1497, 113.4, 17.7, "Sedan", 5),
            ("Venue", 10.0, 1197, 81.8, 17.5, "SUV", 5),
            ("Grand i10 Nios", 6.8, 1197, 81.8, 20.7, "Hatchback", 5),
            ("Tucson", 32.0, 1999, 153.8, 12.9, "SUV", 5)
        ],
        "Honda": [
            ("City", 13.5, 1498, 119.3, 17.8, "Sedan", 5),
            ("Amaze", 8.2, 1199, 88.5, 18.6, "Sedan", 5),
            ("Civic", 22.0, 1799, 139.0, 16.5, "Sedan", 5),
            ("WR-V", 10.2, 1199, 88.7, 16.5, "SUV", 5)
        ],
        "Toyota": [
            ("Innova Crysta", 24.0, 2393, 147.5, 15.1, "MUV", 7),
            ("Fortuner", 38.0, 2755, 201.1, 10.0, "SUV", 7),
            ("Glanza", 8.4, 1197, 88.5, 22.3, "Hatchback", 5),
            ("Urban Cruiser", 11.0, 1462, 103.2, 17.0, "SUV", 5),
            ("Camry", 46.0, 2487, 175.7, 19.1, "Sedan", 5)
        ],
        "Tata": [
            ("Nexon", 11.5, 1199, 118.2, 17.4, "SUV", 5),
            ("Harrier", 19.0, 1956, 167.6, 16.3, "SUV", 5),
            ("Safari", 21.0, 1956, 167.6, 16.1, "SUV", 7),
            ("Altroz", 8.0, 1199, 84.8, 19.3, "Hatchback", 5),
            ("Tiago", 6.2, 1199, 84.8, 20.0, "Hatchback", 5),
            ("Punch", 8.5, 1199, 86.6, 18.8, "SUV", 5)
        ],
        "Mahindra": [
            ("Thar", 16.0, 1997, 150.0, 15.2, "SUV", 4),
            ("Scorpio-N", 18.5, 2198, 172.4, 14.0, "SUV", 7),
            ("XUV700", 22.0, 1997, 197.1, 13.0, "SUV", 7),
            ("XUV300", 11.0, 1197, 108.6, 17.0, "SUV", 5),
            ("Bolero", 10.0, 1493, 74.9, 16.0, "SUV", 7)
        ],
        "Kia": [
            ("Seltos", 15.0, 1497, 113.4, 16.5, "SUV", 5),
            ("Sonet", 10.5, 1197, 81.8, 18.4, "SUV", 5),
            ("Carens", 14.0, 1497, 113.4, 16.5, "MUV", 7)
        ],
        "Volkswagen": [
            ("Polo", 8.5, 999, 108.6, 18.2, "Hatchback", 5),
            ("Vento", 11.5, 999, 108.6, 17.6, "Sedan", 5),
            ("Taigun", 15.5, 999, 113.9, 18.1, "SUV", 5),
            ("Virtus", 14.8, 999, 113.9, 19.4, "Sedan", 5)
        ],
        "BMW": [
            ("3 Series", 48.0, 1998, 254.7, 16.1, "Sedan", 5),
            ("5 Series", 68.0, 1995, 187.7, 17.4, "Sedan", 5),
            ("X1", 45.0, 1995, 147.5, 19.2, "SUV", 5),
            ("X5", 95.0, 2993, 281.6, 13.3, "SUV", 5)
        ],
        "Mercedes-Benz": [
            ("C-Class", 55.0, 1993, 201.1, 16.9, "Sedan", 5),
            ("E-Class", 75.0, 1950, 194.0, 15.0, "Sedan", 5),
            ("GLA", 48.0, 1950, 187.7, 17.9, "SUV", 5)
        ]
    }

    records = []
    brands = list(brand_models.keys())
    brand_probs = [0.22, 0.18, 0.10, 0.12, 0.12, 0.10, 0.08, 0.04, 0.02, 0.02]

    current_year = 2026

    for _ in range(n_samples):
        brand = np.random.choice(brands, p=brand_probs)
        models_list = brand_models[brand]
        model_info = models_list[np.random.choice(len(models_list))]
        model_name, base_price, engine, power, mileage, body_type, seats = model_info

        # Year distribution: 2011 to 2024
        year = int(np.random.choice(
            range(2011, 2025),
            p=[0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.11, 0.10, 0.08, 0.05, 0.03]
        ))
        age = current_year - year

        # Kilometers driven based on age + noise
        avg_yearly_km = np.random.uniform(7000, 16000)
        km_driven = int(max(4000, age * avg_yearly_km + np.random.normal(0, 7000)))

        # Fuel type
        fuel_choices = ["Petrol", "Diesel", "CNG"]
        fuel_probs = [0.55, 0.40, 0.05]
        if brand in ["BMW", "Mercedes-Benz"]:
            fuel_choices = ["Petrol", "Diesel"]
            fuel_probs = [0.50, 0.50]
        fuel_type = np.random.choice(fuel_choices, p=fuel_probs)

        # Transmission
        if brand in ["BMW", "Mercedes-Benz"]:
            transmission = "Automatic"
        else:
            trans_prob = 0.35 if year >= 2020 else 0.20
            transmission = np.random.choice(["Manual", "Automatic"], p=[1 - trans_prob, trans_prob])

        # Owner count correlated with age
        if age <= 2:
            owner = np.random.choice(["First Owner", "Second Owner"], p=[0.92, 0.08])
        elif age <= 5:
            owner = np.random.choice(["First Owner", "Second Owner", "Third Owner"], p=[0.70, 0.26, 0.04])
        elif age <= 8:
            owner = np.random.choice(["First Owner", "Second Owner", "Third Owner", "Fourth & Above"], p=[0.45, 0.40, 0.12, 0.03])
        else:
            owner = np.random.choice(["First Owner", "Second Owner", "Third Owner", "Fourth & Above"], p=[0.25, 0.45, 0.22, 0.08])

        # Slight noise on technical specs for realistic variations
        mileage_kmpl = round(float(mileage * np.random.uniform(0.92, 1.05)), 1)
        engine_cc = int(engine + np.random.choice([-10, 0, 10]))
        max_power = round(float(power * np.random.uniform(0.96, 1.04)), 1)

        # Realistic Depreciation Price Model in Lakhs (INR)
        # Annual depreciation: ~8% to 11% compounded
        # Mileage factor: -0.3% per 10,000 km
        # Owner factor: 2nd owner -8%, 3rd -16%, 4th -24%
        # Transmission: Automatic +8% premium
        # Brand retention: Toyota/Maruti retain slightly higher value; Luxury brands depreciate faster in %

        depreciation_rate = 0.095
        if brand in ["Toyota", "Maruti Suzuki"]:
            depreciation_rate = 0.082
        elif brand in ["BMW", "Mercedes-Benz"]:
            depreciation_rate = 0.135

        # Compound depreciation
        depreciated_val = base_price * ((1 - depreciation_rate) ** age)

        # Mileage penalty
        km_penalty = (km_driven / 10000.0) * 0.015 * base_price
        depreciated_val -= km_penalty

        # Owner penalty
        owner_discounts = {
            "First Owner": 1.0,
            "Second Owner": 0.90,
            "Third Owner": 0.80,
            "Fourth & Above": 0.70
        }
        depreciated_val *= owner_discounts.get(owner, 0.9)

        # Transmission bonus
        if transmission == "Automatic":
            depreciated_val *= 1.07

        # Fuel factor
        if fuel_type == "Diesel":
            depreciated_val *= 1.04
        elif fuel_type == "CNG":
            depreciated_val *= 0.96

        # Market variance noise (+/- 6%)
        noise = np.random.normal(1.0, 0.05)
        selling_price = max(0.9, depreciated_val * noise)
        selling_price = round(selling_price, 2)

        records.append({
            "brand": brand,
            "model": model_name,
            "year": year,
            "selling_price": selling_price,
            "km_driven": km_driven,
            "fuel_type": fuel_type,
            "transmission": transmission,
            "owner": owner,
            "mileage_kmpl": mileage_kmpl,
            "engine_cc": engine_cc,
            "max_power_bhp": max_power,
            "seats": seats
        })

    df = pd.DataFrame(records)

    # Introduce a few realistic messy entries (missing values & outliers) to simulate raw data
    # that the data ingestion & cleaning pipeline will handle
    n_missing = int(len(df) * 0.015)
    missing_indices = np.random.choice(df.index, n_missing, replace=False)
    for idx in missing_indices:
        col = np.random.choice(["mileage_kmpl", "engine_cc", "max_power_bhp"])
        df.loc[idx, col] = np.nan

    # Add duplicate rows
    dups = df.sample(25, random_state=random_state)
    df = pd.concat([df, dups], ignore_index=True)

    return df

if __name__ == "__main__":
    out_dir = "/Users/rohan/.gemini/antigravity/scratch/used-car-price-estimator/data"
    os.makedirs(out_dir, exist_ok=True)
    df = generate_used_car_data(3800)
    out_path = os.path.join(out_dir, "used_cars.csv")
    df.to_csv(out_path, index=False)
    print(f"Generated {len(df)} car records and saved to {out_path}")
