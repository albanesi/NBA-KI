import http.client
import json
from pymongo import MongoClient
import time

# === MongoDB-Verbindung ===
mongo_uri = "mongodb+srv://admin:1234@cluster0.88lshmb.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(mongo_uri)
db = client["LN1"]
collection = db["NBA-Games"]

# === API-Verbindung ===
headers = {
    'x-rapidapi-key': "d817ac6414mshef4ccd567ee1d1cp119238jsn2a4445ca30d9",
    'x-rapidapi-host': "api-nba-v1.p.rapidapi.com"
}

# === Schleife über Seasons ===
for season in range(2015, 2025):
    print(f"🔄 Hole Spiele für Saison {season}...")
    conn = http.client.HTTPSConnection("api-nba-v1.p.rapidapi.com")
    conn.request("GET", f"/games?season={season}", headers=headers)
    res = conn.getresponse()
    data = res.read()

    try:
        games = json.loads(data)
        response = games.get("response", [])

        if response:
            # Optional: Saison in jedes Spiel einfügen (für spätere Queries)
            for game in response:
                game["season"] = season

            collection.insert_many(response)
            print(f"✅ {len(response)} Spiele für Saison {season} gespeichert.")
        else:
            print(f"⚠️ Keine Spiele für Saison {season} erhalten.")
    except Exception as e:
        print(f"❌ Fehler bei Saison {season}: {e}")

    # Etwas warten, um Rate Limits zu vermeiden
    time.sleep(1)
