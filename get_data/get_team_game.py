import requests
import pandas as pd

# Trage hier deinen RapidAPI-Key ein:
api_key = "d817ac6414mshef4ccd567ee1d1cp119238jsn2a4445ca30d9"

# Header für RapidAPI-Zugriff
headers = {
    "X-RapidAPI-Key": api_key,
    "X-RapidAPI-Host": "api-nba-v1.p.rapidapi.com"
}
team_id = 10  # Golden State Warriors
season = 2023

games_url = f"https://api-nba-v1.p.rapidapi.com/games?season={season}&team={team_id}"
games_response = requests.get(games_url, headers=headers)
games_data = games_response.json()
games_df = pd.json_normalize(games_data["response"])
pd.set_option('display.max_columns', None)

print(games_df.head())
