from flask import Flask, jsonify
import requests
import os
import time

app = Flask(__name__)

cache = {
    "data": {},
    "last_updated": 0
}

API_URL = "https://golf-leaderboard.p.rapidapi.com/masters"
HEADERS = {
    "X-RapidAPI-Key": "4b9a8ce3c2mshb857fff0fa65ccbp18968fjsn469673205eb9",
    "X-RapidAPI-Host": "golf-leaderboard.p.rapidapi.com"
}

@app.route("/api/scores")
def get_scores():
    now = time.time()

    if now - cache["last_updated"] < 600:
        return jsonify(cache["data"])

    try:
        res = requests.get(API_URL, headers=HEADERS)
        res.raise_for_status()
        leaderboard = res.json()

        players = {}
        for player in leaderboard.get("leaderboard", []):
            name = player.get("player", {}).get("full_name", "Unknown")
            score = player.get("score", 999)
            status = player.get("status", "")

            if status.upper() == "CUT":
                score += 160

            players[name] = score

        cache["data"] = players
        cache["last_updated"] = now

        return jsonify(players)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
