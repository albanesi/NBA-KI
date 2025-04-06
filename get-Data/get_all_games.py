import http.client
import json
from pymongo import MongoClient
import time

# === MongoDB-Verbindung zu Azure ===
mongo_uri = "mongodb+srv://albanese11:Microsoft1@nba-cosmosdb.global.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"
client = MongoClient(mongo_uri)
db = client["LN1"]
collection = db["NBA-Games"]

# === RapidAPI Key & Host ===
headers = {
    'x-rapidapi-key': "d817ac6414mshef4ccd567ee1d1cp119238jsn2a4445ca30d9",
    'x-rapidapi-host': "api-nba-v1.p.rapidapi.com"
}

# === Alle Spiele von 2015 bis 2024 abrufen ===
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
            for game in response:
                game["season"] = season  # für spätere Filter
            collection.insert_many(response)
            print(f"✅ {len(response)} Spiele für Saison {season} gespeichert.")
        else:
            print(f"⚠️ Keine Spiele für Saison {season} erhalten.")
    except Exception as e:
        print(f"❌ Fehler bei Saison {season}: {e}")

    # Rate-Limit-Vermeidung
    time.sleep(1)
