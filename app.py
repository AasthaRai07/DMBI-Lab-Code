"""
Flask Web Dashboard for Android Malware Detection
DMBI Lab Project - NATICUSdroid Dataset
"""
import os
import json
import joblib
import numpy as np
from flask import Flask, render_template, jsonify, request, send_from_directory

app = Flask(__name__, template_folder="templates", static_folder="static")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
EXP10_DIR = os.path.join(BASE_DIR, "experiments", "exp10")

# Load models and metadata
rf_model = None
dt_model = None
features = []
metrics_data = {}
tree_rules = ""

try:
    rf_model = joblib.load(os.path.join(OUTPUTS_DIR, "rf_model.joblib"))
    dt_model = joblib.load(os.path.join(OUTPUTS_DIR, "dt_model.joblib"))
    features = joblib.load(os.path.join(OUTPUTS_DIR, "features.joblib"))
except Exception as e:
    print(f"Warning: Could not load trained models: {e}")

try:
    with open(os.path.join(OUTPUTS_DIR, "metrics.json"), "r") as f:
        metrics_data = json.load(f)
except Exception as e:
    print(f"Warning: Could not load metrics: {e}")

try:
    with open(os.path.join(OUTPUTS_DIR, "decision_tree_rules.txt"), "r") as f:
        tree_rules = f.read()
except Exception as e:
    print(f"Warning: Could not load tree rules: {e}")


@app.route("/")
def index():
    return render_template(
        "index.html",
        metrics=metrics_data,
        features=features,
        rules=tree_rules
    )


@app.route("/outputs/<path:filename>")
def serve_output(filename):
    return send_from_directory(OUTPUTS_DIR, filename)


@app.route("/exp10/<path:filename>")
def serve_exp10(filename):
    return send_from_directory(EXP10_DIR, filename)


@app.route("/api/metrics", methods=["GET"])
def get_metrics():
    return jsonify(metrics_data)


@app.route("/api/features", methods=["GET"])
def get_features():
    top_importances = []
    if rf_model is not None and len(features) > 0:
        importances = rf_model.feature_importances_
        sorted_idx = np.argsort(importances)[::-1]
        for idx in sorted_idx:
            top_importances.append({
                "name": features[idx],
                "importance": round(float(importances[idx]), 5)
            })
    return jsonify({
        "total": len(features),
        "features": features,
        "ranked_features": top_importances
    })


@app.route("/api/predict", methods=["POST"])
def predict():
    if rf_model is None or dt_model is None or not features:
        return jsonify({"error": "Models not loaded"}), 500

    data = request.get_json() or {}
    selected_perms = set(data.get("permissions", []))

    # Construct input vector (86 binary features)
    x_input = np.zeros((1, len(features)), dtype=int)
    active_features = []
    for i, feat in enumerate(features):
        if feat in selected_perms:
            x_input[0, i] = 1
            active_features.append(feat)

    # Inferences
    rf_proba = float(rf_model.predict_proba(x_input)[0, 1])
    rf_pred = int(rf_model.predict(x_input)[0])
    dt_pred = int(dt_model.predict(x_input)[0])

    # Determine risk category
    if rf_proba >= 0.75:
        risk_level = "Critical Malware Threat"
        risk_color = "red"
    elif rf_proba >= 0.50:
        risk_level = "High Suspicion (Probable Malware)"
        risk_color = "orange"
    elif rf_proba >= 0.25:
        risk_level = "Moderate Caution (Elevated Permissions)"
        risk_color = "yellow"
    else:
        risk_level = "Low Risk (Likely Benign)"
        risk_color = "green"

    return jsonify({
        "random_forest": {
            "prediction": rf_pred,
            "prediction_label": "Malware" if rf_pred == 1 else "Benign",
            "malware_probability": round(rf_proba * 100, 2),
            "risk_level": risk_level,
            "risk_color": risk_color
        },
        "decision_tree": {
            "prediction": dt_pred,
            "prediction_label": "Malware" if dt_pred == 1 else "Benign"
        },
        "active_permission_count": len(active_features),
        "active_permissions": active_features
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

