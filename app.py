from flask import Flask, request, jsonify, render_template
import pickle
import numpy as np

# ─── Load Model ───
with open("model.pkl", "rb") as f:
    model_data = pickle.load(f)

model = model_data['model']
scaler = model_data['scaler']
encoders = model_data['encoders']
severity_encoder = model_data['severity_encoder']
feature_cols = model_data['feature_cols']

# ─── Flask App ───
#app = Flask(__name__)
app = Flask(__name__, static_folder='assets', static_url_path='/assets')

# Render frontend
@app.route("/")
def home():
    return render_template("index.html")

# Predict severity
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.json  # Receive JSON from frontend

        # ─── Extract features in order ───
        features = []
        for col in feature_cols:
            val = data.get(col)

            # Apply encoding for categorical variables
            if col in encoders:
                encoder = encoders[col]
                val = encoder.transform([val])[0]
            features.append(val)

        # Scale numeric features (if scaler exists)
        features = np.array(features).reshape(1, -1)
        if scaler:
            features = scaler.transform(features)

        # Make prediction
        pred_class = model.predict(features)[0]
        pred_prob = model.predict_proba(features)[0]

        severity = severity_encoder.inverse_transform([pred_class])[0]
        confidence = round(np.max(pred_prob) * 100, 2)

        return jsonify({
            "severity": severity,
            "confidence": confidence
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)