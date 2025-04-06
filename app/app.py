import os
from flask import Flask, render_template
from pymongo import MongoClient
import joblib
import numpy as np

# Flask App starten
app = Flask(__name__)



# === MongoDB-Verbindung ===
mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017/")
client = MongoClient(mongo_uri)
db = client["LN1"]
teams_col = db["NBA-Teams"]
stats_col = db["NBA-TrainingData"]  # 2024-Daten für Prediction

# === Modell laden
model = joblib.load("nba_champion_model.pkl")
features = ["wins", "losses", "winPct", "conferenceRank", "divisionRank"]

@app.route("/")
def home():
    teams = list(teams_col.find({}, {"_id": 0, "name": 1, "code": 1, "logo": 1}))
    return render_template("index.html", teams=teams)


@app.route("/prediction/<team_code>")
def prediction(team_code):
    # 2024er Stats holen
    team_stats = stats_col.find_one({"team_code": team_code.upper(), "season": "2024"})
    if not team_stats:
        return render_template("prediction.html", error="Keine Stats für dieses Team gefunden.", team=None)

    # Feature-Vektor vorbereiten
    x = np.array([[team_stats[f] for f in features]])
    probability = model.predict_proba(x)[0][1] * 100  # Wahrscheinlichkeit als %

    return render_template("prediction.html", team=team_stats, prediction=round(probability, 2))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

