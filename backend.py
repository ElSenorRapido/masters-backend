from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

@app.route("/api/scores")
def get_scores():
    url = "http://www.espn.com/golf/leaderboard"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table")
        players = {}

        for row in table.find_all("tr")[1:]:
            cols = row.find_all("td")
            if len(cols) < 2:
                continue

            name = cols[0].get_text(strip=True)
            raw_score = cols[1].get_text(strip=True)

            if raw_score == "E":
                score = 0
            elif raw_score.startswith("+") or raw_score.startswith("-"):
                try:
                    score = int(raw_score)
                except:
                    continue
            else:
                try:
                    score = int(raw_score)
                except:
                    continue

            players[name] = score

        return jsonify(players)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
