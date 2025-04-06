import os
from flask import Flask, render_template
from pymongo import MongoClient
import joblib
import numpy as np
import sys
import logging

logging.basicConfig(level=logging.INFO)

# === Flask App starten ===
app = Flask(__name__)

# === MongoDB-Verbindung ===
client = MongoClient("mongodb+srv://albanese11:Kosova11@nba-cosmosdb.global.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000")
db = client["LN1"]
teams_col = db["NBA-Teams"]
stats_col = db["NBA-Standings"]  # 2023-Daten für Prediction

# === Modell laden ===
model = joblib.load("../nba_champion_model.pkl")
features = ["wins", "losses", "winPct", "conferenceRank", "divisionRank"]

# === Funktion zum Logo-Update ===
def update_team_logos():
    logos = {
        "OKC": 'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fcdn.shopify.com%2Fs%2Ffiles%2F1%2F1949%2F1233%2Fproducts%2Fokc-thunder-2_1000x1000.progressive.jpg%3Fv%3D1575428341&f=1&nofb=1&ipt=90b16a7f4906a30b65e1059f25750185c88175d29483ab36515d524605e14ff3&ipo=images',
        "MIA": 'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fwallpaperaccess.com%2Ffull%2F2214394.jpg&f=1&nofb=1&ipt=f4ec0901435fab2674af42c2c1e427777a6b607eb0deda9c74c04a4d5478ef23&ipo=images',
        "MIL": 'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse3.mm.bing.net%2Fth%3Fid%3DOIP.vH4s8IvEyMPLv35Yk33INAHaEK%26pid%3DApi&f=1&ipt=27bdce032d47e818f31ec8fc2a92d3085b4623a81785a1c2a577c256c4c53ce6&ipo=images',
        "ORL": 'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse1.mm.bing.net%2Fth%3Fid%3DOIP.-s2I1BQg_VwjjnF93Sr6HgHaHa%26pid%3DApi&f=1&ipt=a63ab70067c05f8836330792c16a5ecaf1842ba91f01472e65500a168c391e65&ipo=images',
        "PHI": 'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse1.mm.bing.net%2Fth%3Fid%3DOIP._BDKPnN4RTMji4Iibt1adgHaEK%26pid%3DApi&f=1&ipt=cb6830505fd22c9f4167449a648c8d07df08686641d58e1a8d414e0ea2643a7a&ipo=images'
    }

    for code, logo_url in logos.items():
        result = teams_col.update_one({"code": code}, {"$set": {"logo": logo_url}})
        if result.modified_count > 0:
            logging.info(f"✅ Logo für {code} aktualisiert.")
        else:
            logging.warning(f"⚠️ Kein Update für {code} (evtl. bereits aktuell oder nicht gefunden).")

# === Routen ===
@app.route("/")
def home():
    teams = list(teams_col.find({}, {"_id": 0, "name": 1, "code": 1, "logo": 1}))
    return render_template("index.html", teams=teams)

@app.route("/prediction/<team_code>")
def prediction(team_code):
    logging.info("🏀 Anfrage für: " + team_code)
    team_stats = stats_col.find_one({"team_code": team_code.upper(), "season": "2023"})
    
    if not team_stats:
        return render_template("prediction.html", error="Keine Stats für dieses Team gefunden.", team=None)

    x = np.array([[team_stats[f] for f in features]])
    probability = model.predict_proba(x)[0][1] * 100

    return render_template("prediction.html", team=team_stats, prediction=round(probability, 2))

# === App starten ===
if __name__ == "__main__":
    update_team_logos()  # Logos einmalig beim Start aktualisieren
    app.run(host="0.0.0.0", port=80)
