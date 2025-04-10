from flask import Flask, jsonify
import requests
import os

app = Flask(__name__)

@app.route("/api/scores")
def get_scores():
    url = "https://site.api.espn.com/apis/site/v2/sports/golf/pga-tour/leaderboard"

    try:
        response = requests.get(url)
        data = response.json()

        players = {}

        competitors = data["events"][0]["competitions"][0]["competitors"]
        for player in competitors:
            name = player["athlete"]["displayName"]
            status = player["status"]["type"]["description"]
            raw_score = player.get("score")

            # ESPN sometimes lists score as string, sometimes number
            try:
                score = int(raw_score)
            except:
                score = 0

            # Apply 80-stroke penalty for rounds 3 & 4 if CUT
            if status == "CUT":
                score += 160

            players[name] = score

        return jsonify(players)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Required for Render to expose the port
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
