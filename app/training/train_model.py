import pandas as pd
from pymongo import MongoClient
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

# === MongoDB-Verbindung ===
mongo_uri = "mongodb+srv://admin:1234@cluster0.88lshmb.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(mongo_uri)
db = client["LN1"]
collection = db["NBA-TrainingData"]

# === Daten aus DB holen
docs = list(collection.find({"season": {"$ne": "2024"}}))  # 2024 NICHT im Training!
df = pd.DataFrame(docs)

# === Features und Ziel
features = ["wins", "losses", "winPct", "conferenceRank", "divisionRank"]
X = df[features]
y = df["champion"]

# === Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

# === Modell trainieren
model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
model.fit(X_train, y_train)

# === Modell evaluieren
y_pred = model.predict(X_test)
print("=== Model Evaluation ===")
print(classification_report(y_test, y_pred, digits=3))

# === Modell speichern
joblib.dump(model, "nba_champion_model.pkl")
print("✅ Modell gespeichert als nba_champion_model.pkl")
