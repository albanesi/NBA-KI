import http.client
import json
from pymongo import MongoClient
import time

# === MongoDB-Verbindung ===
mongo_uri = "mongodb+srv://admin:1234@cluster0.88lshmb.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(mongo_uri)
db = client["LN1"]  

teams_collection = db["NBA-Teams"]
players_collection = db["NBA-Players"]

# === API Setup ===
headers = {
    'x-rapidapi-key': "d817ac6414mshef4ccd567ee1d1cp119238jsn2a4445ca30d9",
    'x-rapidapi-host': "api-nba-v1.p.rapidapi.com"
}

# === Alle Team-IDs aus der DB laden ===
teams = list(teams_collection.find({}))
team_ids = [team["id"] for team in teams if "id" in team]

print(f"🔍 {len(team_ids)} Team-IDs geladen")

# === Loop: Für jedes Team und jede Saison Spieler holen ===
for team_id in team_ids:
    for season in range(2015, 2025):
        print(f"🔄 Hole Spieler für Team {team_id}, Saison {season}")
        conn = http.client.HTTPSConnection("api-nba-v1.p.rapidapi.com")
        endpoint = f"/players?team={team_id}&season={season}"

        conn.request("GET", endpoint, headers=headers)
        res = conn.getresponse()
        data = res.read()

        try:
            players = json.loads(data)
            response = players.get("response", [])

            if response:
                for player in response:
                    player["team_id"] = team_id
                    player["season"] = season

                players_collection.insert_many(response)
                print(f"✅ {len(response)} Spieler gespeichert.")
            else:
                print("⚠️ Keine Spieler gefunden.")

        except Exception as e:
            print(f"❌ Fehler bei Team {team_id}, Saison {season}: {e}")

        time.sleep(1)  # API-Limit beachten
