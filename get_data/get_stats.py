import http.client
import json
from pymongo import MongoClient

# === MongoDB-Verbindung ===
mongo_uri = "mongodb+srv://admin:1234@cluster0.88lshmb.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(mongo_uri)
db = client["LN1"]
stats_collection = db["NBA-Stats"]
stats_collection.delete_many({})  # Optional: leeren vor Neuimport

# === API-Verbindung ===
conn = http.client.HTTPSConnection("api-nba-v1.p.rapidapi.com")
headers = {
    'x-rapidapi-key': "d817ac6414mshef4ccd567ee1d1cp119238jsn2a4445ca30d9",
    'x-rapidapi-host': "api-nba-v1.p.rapidapi.com"
}

season = "2024"

# === Step 1: Teams abrufen ===
conn.request("GET", "/teams", headers=headers)
teams_data = conn.getresponse().read()
teams_response = json.loads(teams_data)["response"]

nba_teams = [team for team in teams_response if team.get("nbaFranchise")]

# === Step 2: Standings abrufen (für wins/losses)
conn.request("GET", f"/standings?season={season}&league=standard", headers=headers)
standings_data = conn.getresponse().read()
standings_response = json.loads(standings_data)["response"]

# Mapping team_id → standings info
standings_map = {s["team"]["id"]: s for s in standings_response}

# === Step 3: Für jedes Team: Stats + Standings kombinieren
for team in nba_teams:
    team_id = team["id"]
    team_code = team["code"]
    team_name = team["name"]

    # STATS
    conn.request("GET", f"/teams/statistics?id={team_id}&season={season}", headers=headers)
    stats_raw = conn.getresponse().read()
    stats_response = json.loads(stats_raw).get("response")

    # Defensive Check: manchmal kommt eine leere Liste oder kein Dict
    if not stats_response or not isinstance(stats_response, dict):
        print(f"⚠️ Keine gültigen Stats für {team_name}")
        continue

    stats = stats_response
    stats["team_id"] = team_id
    stats["team_code"] = team_code
    stats["team_name"] = team_name
    stats["season"] = season
    stats["logo"] = team.get("logo")

    # STANDINGS hinzufügen, falls vorhanden
    standing = standings_map.get(team_id)
    if standing:
        stats["wins"] = int(standing["win"]["total"])
        stats["losses"] = int(standing["loss"]["total"])
        stats["winPct"] = float(standing["win"]["percentage"])
        stats["conferenceRank"] = int(standing["conference"]["rank"])
        stats["divisionRank"] = int(standing["division"]["rank"])
    else:
        stats["wins"] = None
        stats["losses"] = None
        stats["winPct"] = None
        stats["conferenceRank"] = None
        stats["divisionRank"] = None

    stats_collection.insert_one(stats)
    print(f"✅ {team_name} gespeichert")

print("🏁 Alle Team-Stats importiert!")
