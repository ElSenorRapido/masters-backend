from flask import Flask, jsonify
import requests
import os
import time

app = Flask(__name__)

# Store the last response and timestamp
cache = {
    "data": {},
    "last_updated": 0
}

SLASH_GOLF_API_KEY = "4b9a8ce3c2mshb857fff0fa65ccbp18968fjsn469673205eb9"
API_URL = "https://slashgolf.p.rapidapi.com/v1/events/masters/leaderboard"
HEADERS = {
    "X-RapidAPI-Key": SLASH_GOLF_API_KEY,
    "X-RapidAPI-Host": "slashgolf.p.rapidapi.com"
}

@app.route("/api/scores")
def get_scores():
    now = time.time()

    # If it's been less than 10 minutes (600 sec), return cached
    if now - cache["last_updated"] < 600:
        return jsonify(cache["data"])

    try:
        res = requests.get(API_URL, headers=HEADERS)
        res.raise_for_status()
        leaderboard = res.json()

        players = {}
        for player in leaderboard.get("leaderboard", []):
            name = player.get("player", {}).get("full_name", "Unknown")
            score = player.get("score", None)
            status = player.get("status", "")

            if score is not None:
                # Optional: Add penalty for CUT players
                if status.upper() == "CUT":
                    score += 160
                players[name] = score

        # Update cache
        cache["data"] = players
        cache["last_updated"] = now

        return jsonify(players)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# For Render to assign port
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
