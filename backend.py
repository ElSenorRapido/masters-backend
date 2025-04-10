from flask import Flask, jsonify
from pga_live_leaderboard import Leaderboard
from rapidfuzz import process
import os
import time

app = Flask(__name__)

# Your original picks, from the pool
# You can include every name as entered, even with typos
player_pool = [
    "Scottie Scheffler", "Rory McIlroy", "John Rahm", "Xander Schauffle",
    "Brook Koepka", "Tony Finau", "Juston Thomas", "Ludvig Aaberg",
    "Bryson DeChambeu", "Max Homa", "Wyndam Clark", "Jaoquin Nieman",
    "Sam Burns", "Zach Johnson", "Akshay Bhatia", "JJ Spaun",
    "Justin Rose", "Lucas Glover", "Daniel Berger", "Phil Mickelson",
    "Cameron Davis", "Billy Horschel", "Dustin Johnson", "Viktor Hovland",
    "Russell Henley", "Sungjae Im", "Corey Conners", "Sepp Straka",
    "Aaron Rai", "Shane Lowry", "Taylor Pendrith", "Robert MacIntyre",
    "JT Poston", "Harris English", "Nicolas Echavarria", "Patrick Reed",
    "Chris Kirk", "Sahith Theegala", "Keegan Bradley", "Danny Willett",
    "Adam Scott", "Nicolai Hojgaard", "Maverick McNealy", "Colin Morikawa",
    "Denny McCarthy", "Matt Fitzpatrick", "Hideki Matsuyama"
]

cache = {
    "data": {},
    "last_updated": 0
}

@app.route("/api/scores")
def get_scores():
    now = time.time()

    # Use cache if within 5 minutes
    if now - cache["last_updated"] < 300:
        return jsonify(cache["data"])

    try:
        lb = Leaderboard()
        data = lb.get_json()

        all_pga_players = {p["player_name"]: p.get("total", "999") for p in data.get("players", [])}

        matched_scores = {}

        for user_entry in player_pool:
            match, score = process.extractOne(user_entry, all_pga_players.keys())
            matched_score_raw = all_pga_players.get(match)

            try:
                matched_score = 0 if matched_score_raw == "E" else int(matched_score_raw)
            except:
                matched_score = 999

            matched_scores[user_entry] = {
                "matched_name": match,
                "score": matched_score
            }

        # Add full leaderboard too
        full_scores = {
            name: 0 if raw == "E" else int(raw) if str(raw).lstrip("+-").isdigit() else 999
            for name, raw in all_pga_players.items()
        }

        cache["data"] = {
            "matched_pool": matched_scores,
            "full_leaderboard": full_scores
        }
        cache["last_updated"] = now

        return jsonify(cache["data"])

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
