import http.client
import json
from pymongo import MongoClient

# === MongoDB-Verbindung ===
mongo_uri = "mongodb+srv://admin:1234@cluster0.88lshmb.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(mongo_uri)
db = client["LN1"]
collection = db["NBA-Teams"]

# Optional: Collection leeren
# collection.delete_many({})

# === API-Verbindung ===
conn = http.client.HTTPSConnection("api-nba-v1.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "d817ac6414mshef4ccd567ee1d1cp119238jsn2a4445ca30d9",
    'x-rapidapi-host': "api-nba-v1.p.rapidapi.com"
}

# === Teams abrufen ===
conn.request("GET", "/teams", headers=headers)
res = conn.getresponse()
data = res.read()

teams = json.loads(data)

# === Optional: Teamstruktur anzeigen (erste 2 Teams)
for team in teams["response"][:2]:
    print(json.dumps(team, indent=2))

# === Nur NBA-Teams (wenn vorhanden)
nba_teams = [team for team in teams["response"] if team.get("nbaFranchise") == True]

# === In MongoDB speichern ===
collection.insert_many(nba_teams)
print(f"✅ {len(nba_teams)} NBA-Teams erfolgreich gespeichert.")
