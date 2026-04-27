from flask import Flask, request, jsonify
from flask_cors import CORS

from saba_core import analyze_session, load_model

app = Flask(__name__)
CORS(app)

model = load_model()

@app.route("/")
def home():
    return "SABA AI Model is Running"

@app.route("/predict", methods=["POST", "OPTIONS"])
def predict():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    data = request.get_json()
    result = analyze_session(data, model=model)

    return jsonify({
        "decision": result["decision"],
        "decision_title": result["decision_title"],
        "confidence": result["confidence"],
        "reason": result["reason"],
        "recommendation": result["recommendation"],
    })

if __name__ == "__main__":
    app.run(debug=True)
