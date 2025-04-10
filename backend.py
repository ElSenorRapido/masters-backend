from flask import Flask, jsonify
import requests
import os
import time

app = Flask(__name__)

# Cache to limit API calls (refresh every 10 minutes)
cache = {
    "data": {},
    "last_updated": 0
}

# API endpoint and auth
API_URL = "https://live-golf-data.p.rapidapi.com/tournament"
HEADERS = {
    "X-RapidAPI-Key": "4b9a8ce3c2mshb857fff0fa65ccbp18968fjsn469673205eb9",
    "X-RapidAPI-Host": "live-golf-data.p.rapidapi.com"
}
PARAMS = {
    "orgId": "1",     # PGA
    "tournId": "475", # Masters
    "year": "2024"    # ✅ 2025 Masters
}

@app.route("/api/scores")
def get_scores():
    now = time.time()

    # Return cached results if within 10 minutes
    if now - cache["last_updated"] < 600:
        return jsonify(cache["data"])

    try:
        res = requests.get(API_URL, headers=HEADERS, params=PARAMS)
        res.raise_for_status()
        data = res.json()

        players = {}

        leaderboard = data.get("leaderboard", {}).get("players", [])
        for p in leaderboard:
            name = p.get("player_name", "Unknown")
            score = p.get("total_to_par")

            # Convert "E" to 0, try to parse as int
            if score == "E":
                score = 0
            try:
                score = int(score)
            except:
                score = 999  # fallback for invalid or missing scores

            players[name] = score

        # Update the cache
        cache["data"] = players
        cache["last_updated"] = now
        return jsonify(players)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Needed by Render or any cloud host
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
