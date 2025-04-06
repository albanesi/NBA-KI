import requests
import pandas as pd
from pymongo import MongoClient

# === MongoDB-Verbindung (Azure) ===
mongo_uri = "mongodb+srv://albanese11:Kosova11@nba-cosmosdb.global.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"
client = MongoClient(mongo_uri)
db = client["LN1"]
collection = db["NBA-TeamGames"]

# === Team und Saison definieren ===
team_id = 10  # Golden State Warriors
season = 2023

# === RapidAPI-Zugang ===
api_key = "d817ac6414mshef4ccd567ee1d1cp119238jsn2a4445ca30d9"
headers = {
    "X-RapidAPI-Key": api_key,
    "X-RapidAPI-Host": "api-nba-v1.p.rapidapi.com"
}

# === API-Anfrage ===
games_url = f"https://api-nba-v1.p.rapidapi.com/games?season={season}&team={team_id}"
games_response = requests.get(games_url, headers=headers)
games_data = games_response.json()

# === Normalisieren & Anzeigen (optional)
games_df = pd.json_normalize(games_data["response"])
pd.set_option('display.max_columns', None)
print(games_df.head())

# === In MongoDB speichern
if games_data.get("response"):
    for game in games_data["response"]:
        game["team_id"] = team_id
        game["season"] = season
    collection.insert_many(games_data["response"])
    print(f"✅ {len(games_data['response'])} Spiele für Team-ID {team_id} gespeichert.")
else:
    print("⚠️ Keine Spiele gefunden.")
