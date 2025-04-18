from flask import Flask, request, jsonify, render_template
import pandas as pd
import joblib
from datetime import datetime

# Load trained models
reg_model = joblib.load("parking_regression_model.pkl")
cls_model = joblib.load("parking_classification_model.pkl")
encoded_columns = joblib.load("encoded_columns.pkl")

# Create Flask app
application = Flask(__name__)

# Home route (optional: show index.html if you build frontend)
@app.route("/")
def index():
    return render_template("index.html")

#  API endpoint
@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    location = data.get("location")

    #  Automatically get current time and day
    now = datetime.now()
    current_day = now.strftime("%A")
    current_time = now.strftime("%H:%M")

    #  Round time to model block
    model_blocks = ["10:00", "12:00", "14:00", "16:00", "18:00"]
    model_times = [datetime.strptime(t, "%H:%M") for t in model_blocks]
    user_time = datetime.strptime(current_time, "%H:%M")
    closest_block = min(model_times, key=lambda block: abs(block - user_time)).strftime("%H:%M")

    # Build one-hot encoded input
    input_dict = dict.fromkeys(encoded_columns, 0)
    if f"Day_{current_day}" in input_dict:
        input_dict[f"Day_{current_day}"] = 1
    if f"Time_{closest_block}" in input_dict:
        input_dict[f"Time_{closest_block}"] = 1
    if f"Location_{location}" in input_dict:
        input_dict[f"Location_{location}"] = 1

    user_df = pd.DataFrame([input_dict])[encoded_columns]

    # Predict
    predicted_class = cls_model.predict(user_df)[0]
    predicted_prob = cls_model.predict_proba(user_df)[0]
    predicted_spaces = reg_model.predict(user_df)[0]

    availability_map = {0: "Full", 1: "Moderate", 2: "Empty"}
    result = {
        "day": current_day,
        "time": closest_block,
        "location": location,
        "availability": availability_map[predicted_class],
        "confidence": round(max(predicted_prob) * 100, 1),
        "spaces": int(round(predicted_spaces))
    }

    return jsonify(result)

app = app
