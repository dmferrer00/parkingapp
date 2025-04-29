import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
import joblib
from datetime import datetime

# Load cleaned data
print(" Loading cleaned parking data...")
df = pd.read_csv("cleaned_parking_data_all_days.csv")

# Calculate total available spaces
df["Available Spaces"] = df[['Student', 'Fac/Staff', 'Visitor/Meter', 'Reserved', 'Disabled', 'Reduced']].sum(axis=1)

# Remove rows with 0 available spaces
df = df[df["Available Spaces"] > 0].copy()

# Create Availability Category
def categorize_availability(spaces):
    if spaces <= 10:
        return "Full"
    elif 11 <= spaces <= 50:
        return "Moderate"
    else:
        return "Empty"

df["Availability Category"] = df["Available Spaces"].apply(categorize_availability)
df["Availability Category"] = df["Availability Category"].map({"Full": 0, "Moderate": 1, "Empty": 2})

#  Day, Time, Location
df = df[["Day", "Time", "Location", "Available Spaces", "Availability Category"]]

# One-hot encode categorical variables
df_encoded = pd.get_dummies(df, columns=["Day", "Time", "Location"], drop_first=False)

# Save the correct input features
X_input_features = df_encoded.drop(columns=["Available Spaces", "Availability Category"])
encoded_columns = X_input_features.columns

# Targets
y_reg = df_encoded["Available Spaces"]
y_cls = df_encoded["Availability Category"]

# Train models
print("Training models...")
reg_model = RandomForestRegressor(n_estimators=100, random_state=42)
reg_model.fit(X_input_features, y_reg)

cls_model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
cls_model.fit(X_input_features, y_cls)

# Save models
joblib.dump(reg_model, "parking_regression_model.pkl")
joblib.dump(cls_model, "parking_classification_model.pkl")
joblib.dump(encoded_columns, "encoded_columns.pkl")

print("Models trained and saved successfully!")
