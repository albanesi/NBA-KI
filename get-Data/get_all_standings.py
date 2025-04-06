import http.client
import json
from pymongo import MongoClient

# === MongoDB-Verbindung (Azure) ===
mongo_uri = "mongodb+srv://albanese11:Microsoft1@nba-cosmosdb.global.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"
client = MongoClient(mongo_uri)
db = client["LN1"]
stats_collection = db["NBA-Standings"]
stats_collection.delete_many({})  # optional: leeren

# === Manuelle Champions ===
champions = {
    "2018": "GSW",
    "2019": "TOR",
    "2020": "LAL",
    "2021": "MIL",
    "2022": "GSW",
    "2023": "DEN"
}

# === API-Verbindung ===
conn = http.client.HTTPSConnection("api-nba-v1.p.rapidapi.com")
headers = {
    'x-rapidapi-key': "d817ac6414mshef4ccd567ee1d1cp119238jsn2a4445ca30d9",
    'x-rapidapi-host': "api-nba-v1.p.rapidapi.com"
}

# === Teams abrufen
conn.request("GET", "/teams", headers=headers)
teams_data = conn.getresponse().read()
teams_response = json.loads(teams_data)["response"]

team_info_map = {
    t["id"]: {
        "team_code": t["code"],
        "team_name": t["name"],
        "logo": t.get("logo")
    }
    for t in teams_response if t.get("nbaFranchise")
}

# === Saisonweise Standings holen
for season in range(2018, 2025):
    print(f"📅 Lade Daten für Saison {season}...")

    conn.request("GET", f"/standings?season={season}&league=standard", headers=headers)
    standings_data = conn.getresponse().read()
    standings_response = json.loads(standings_data)["response"]

    for entry in standings_response:
        team_id = entry["team"]["id"]
        info = team_info_map.get(team_id)

        if not info:
            print(f"⚠️ Team ID {team_id} nicht gefunden")
            continue

        doc = {
            "team_id": team_id,
            "team_code": info["team_code"],
            "team_name": info["team_name"],
            "logo": info["logo"],
            "season": str(season),
            "wins": int(entry["win"]["total"]),
            "losses": int(entry["loss"]["total"]),
            "winPct": float(entry["win"]["percentage"]),
            "conferenceRank": int(entry["conference"]["rank"]),
            "divisionRank": int(entry["division"]["rank"]),
            "champion": 1 if str(season) in champions and info["team_code"] == champions[str(season)] else 0
        }

        stats_collection.insert_one(doc)
        print(f"✅ {doc['season']} – {doc['team_code']} gespeichert")

print("🏁 Alle Trainingsdaten 2018–2024 erfolgreich importiert!")
