from flask import Flask, render_template, request
import pandas as pd
import joblib
from datetime import datetime

app = Flask(__name__)

# Load model and encodings
df = pd.read_csv("cleaned.csv")
df.fillna(0, inplace=True)
df["Available Spaces"] = df[['Student', 'Fac/Staff', 'Visitor/Meter', 'Reserved', 'Disabled', 'Reduced']].sum(axis=1)
df = df[df["Available Spaces"] > 0].copy()

df["Availability Category"] = df["Available Spaces"].apply(
    lambda x: 0 if x <= 10 else (1 if x <= 50 else 2)
)
df = df[["Day", "Time", "Location", "Available Spaces", "Availability Category"]]
df_encoded = pd.get_dummies(df, columns=["Day", "Time", "Location"], drop_first=False)

X_input_features = df_encoded.drop(columns=["Available Spaces", "Availability Category"])
encoded_columns = X_input_features.columns

# Load models
reg_model = joblib.load("parking_regression_model.pkl")
cls_model = joblib.load("parking_classification_model.pkl")

def map_user_time_to_model_block(user_time_str):
    model_blocks = ["10:00", "12:00", "14:00", "16:00", "18:00"]
    model_times = [datetime.strptime(t, "%H:%M") for t in model_blocks]
    user_time = datetime.strptime(user_time_str, "%H:%M")
    closest_block = min(model_times, key=lambda block: abs(block - user_time))
    return closest_block.strftime("%H:%M")

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        user_day = request.form["day"].title()
        raw_user_time = request.form["time"]
        user_location = request.form["location"].strip()

        try:
            user_time = map_user_time_to_model_block(raw_user_time)
        except ValueError:
            result = "Invalid time format. Please use HH:MM."
            return render_template("index.html", result=result)

        input_dict = dict.fromkeys(encoded_columns, 0)
        if f"Day_{user_day}" in input_dict:
            input_dict[f"Day_{user_day}"] = 1
        if f"Time_{user_time}" in input_dict:
            input_dict[f"Time_{user_time}"] = 1
        if f"Location_{user_location}" in input_dict:
            input_dict[f"Location_{user_location}"] = 1

        user_input_df = pd.DataFrame([input_dict])[encoded_columns]
        predicted_class = cls_model.predict(user_input_df)[0]
        predicted_probs = cls_model.predict_proba(user_input_df)[0]
        confidence = max(predicted_probs) * 100
        predicted_spaces = reg_model.predict(user_input_df)[0]

        availability_map = {0: "Full", 1: "Moderate", 2: "Empty"}
        category_str = availability_map[predicted_class]

        result = {
            "category": category_str,
            "confidence": round(confidence, 1),
            "spaces": round(predicted_spaces),
            "day": user_day,
            "time": user_time,
            "location": user_location
        }

    return render_template("index.html", result=result)
