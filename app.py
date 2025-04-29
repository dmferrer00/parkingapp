from flask import Flask, request, jsonify, render_template
import pandas as pd
import joblib
from datetime import datetime

# Load trained models
reg_model = joblib.load("parking_regression_model.pkl")
cls_model = joblib.load("parking_classification_model.pkl")
encoded_columns = joblib.load("encoded_columns.pkl")

# Create Flask app
app = Flask(__name__)

# Home route 
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    location = data.get("location")

    now = datetime.now()
    current_day = now.strftime("%A")
    current_time = now.strftime("%H:%M")

    model_blocks = ["10:00", "12:00", "14:00", "16:00", "18:00"]
    model_times = [datetime.strptime(t, "%H:%M") for t in model_blocks]
    user_time = datetime.strptime(current_time, "%H:%M")
    closest_block = min(model_times, key=lambda block: abs(block - user_time)).strftime("%H:%M")

    # Build ONLY expected input columns
    input_dict = {col: 0 for col in encoded_columns}

    # Set correct 1s
    if f"Day_{current_day}" in input_dict:
        input_dict[f"Day_{current_day}"] = 1
    if f"Time_{closest_block}" in input_dict:
        input_dict[f"Time_{closest_block}"] = 1
    if f"Location_{location}" in input_dict:
        input_dict[f"Location_{location}"] = 1

    # Create input dataframe
    user_df = pd.DataFrame([input_dict])

    # Make sure column order matches
    user_df = user_df[encoded_columns]

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


if __name__ == "__main__":
    app.run(debug=True)
