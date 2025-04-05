import pandas as pd
from pymongo import MongoClient
from sklearn.linear_model import LogisticRegression
import joblib

# MongoDB-Verbindung
mongo_uri = "mongodb+srv://admin:1234@cluster0.88lshmb.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(mongo_uri)
db = client["LN1"]
collection = db["NBA-Standings"]

# Daten holen
docs = list(collection.find({}))
df = pd.DataFrame(docs)

# Zielvariable definieren (Teams auf Platz 1 = Titelkandidat)
df["label"] = df["conferenceRank"].apply(lambda r: 1 if r == 1 else 0)

# Features
features = ["wins", "losses", "winPct", "conferenceRank", "divisionRank"]
X = df[features]
y = df["label"]

# Modell trainieren
model = LogisticRegression()
model.fit(X, y)

# Modell speichern
joblib.dump(model, "nba_title_model.pkl")
print("✅ Modell gespeichert als nba_title_model.pkl")
