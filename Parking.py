import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_absolute_error, accuracy_score
from datetime import datetime
import joblib
import os



# Load cleaned data
print(" Loading cleaned parking data...")
df = pd.read_csv("cleaned_parking_data_all_days.csv")
print(" Data Loaded! First 5 rows:")
print(df.head())

# Fill missing values
df.fillna(0, inplace=True)

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

# Keep only useful columns
df = df[["Day", "Time", "Location", "Available Spaces", "Availability Category"]]

# One-hot encode
df_encoded = pd.get_dummies(df, columns=["Day", "Time", "Location"], drop_first=False)

# Store training features
X_input_features = df_encoded.drop(columns=["Available Spaces", "Availability Category"])
encoded_columns = X_input_features.columns

# Split datasets
X_reg = X_input_features.copy()
y_reg = df_encoded["Available Spaces"]
X_train_reg, X_test_reg, y_train_reg, y_test_reg = train_test_split(X_reg, y_reg, test_size=0.2, random_state=42)

X_cls = X_input_features.copy()
y_cls = df_encoded["Availability Category"]
X_train_cls, X_test_cls, y_train_cls, y_test_cls = train_test_split(X_cls, y_cls, test_size=0.2, random_state=42)

# Train models
reg_model = RandomForestRegressor(n_estimators=100, random_state=42)
reg_model.fit(X_train_reg, y_train_reg)

cls_model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
cls_model.fit(X_train_cls, y_train_cls)

# Save models
joblib.dump(reg_model, "parking_regression_model.pkl")
joblib.dump(cls_model, "parking_classification_model.pkl")
print(" Models saved to disk!\n")

# Round time 
def map_user_time_to_model_block(user_time_str):
    model_blocks = ["10:00", "12:00", "14:00", "16:00", "18:00"]
    model_times = [datetime.strptime(t, "%H:%M") for t in model_blocks]
    try:
        user_time = datetime.strptime(user_time_str, "%H:%M")
    except ValueError:
        raise ValueError(" Invalid time format. Use HH:MM (e.g., 13:30)")
    closest_block = min(model_times, key=lambda block: abs(block - user_time))
    return closest_block.strftime("%H:%M")

#  prediction loop
while True:
    print("\n Let's predict parking availability!\n")
    valid_days = sorted(df["Day"].unique())
    valid_times = sorted(df["Time"].unique())
    valid_locations = sorted(df["Location"].unique())

    print(" Available Days:", ", ".join(valid_days))
    print(" Model Time Blocks:", ", ".join(valid_times))
    print(" Available Locations (examples):", ", ".join(valid_locations[:5]), "...")

    user_day = input("Enter the day: ").strip().title()
    raw_user_time = input(" Enter your time (e.g. 13:30): ").strip()
    user_location = input(" Enter the parking location: ").strip()

    if user_day not in valid_days or user_location not in valid_locations:
        print(" Invalid input! Try again.")
        continue

    try:
        user_time = map_user_time_to_model_block(raw_user_time)
    except ValueError as e:
        print(e)
        continue
    print(f"Using nearest model time block: {user_time}")

    # Build input vector
    input_dict = dict.fromkeys(encoded_columns, 0)
    if f"Day_{user_day}" in input_dict:
        input_dict[f"Day_{user_day}"] = 1
    if f"Time_{user_time}" in input_dict:
        input_dict[f"Time_{user_time}"] = 1
    if f"Location_{user_location}" in input_dict:
        input_dict[f"Location_{user_location}"] = 1

    user_input_df = pd.DataFrame([input_dict])[encoded_columns]

    # Predict
    predicted_class = cls_model.predict(user_input_df)[0]
    predicted_probs = cls_model.predict_proba(user_input_df)[0]
    confidence = max(predicted_probs) * 100
    predicted_spaces = reg_model.predict(user_input_df)[0]

    availability_map = {0: "Full", 1: "Moderate", 2: "Empty"}
    category_str = availability_map[predicted_class]

    print("\n Prediction Results:")
    print(f" Availability Category: {category_str} (Confidence: {confidence:.1f}%)")
    print(f" Estimated Available Spaces: {round(predicted_spaces)}")

    #  Show real data 
    match = df[
        (df["Day"] == user_day) &
        (df["Time"] == user_time) &
        (df["Location"] == user_location)
    ]

    if not match.empty:
        print(f"\n Real entries for {user_day} @ {user_time} in {user_location}:")
        print(match[["Available Spaces", "Availability Category"]])
    else:
        print("\n No matching historical data for that input in the dataset.")

    repeat = input("\n Want to make another prediction? (yes/no): ").strip().lower()
    if repeat != "yes":
        print(" Thanks for using the parking predictor! Exiting now.")
        break
joblib.dump(encoded_columns, "encoded_columns.pkl")
