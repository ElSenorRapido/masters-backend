from flask import Flask, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import time

app = Flask(__name__)

# Cache to avoid hitting the Sheets API too often
cache = {
    "data": {},
    "last_updated": 0
}

# Path to your downloaded JSON key
GOOGLE_SHEET_CREDENTIALS = "sheets-access.json"  # rename to match your downloaded file
SHEET_URL = "https://docs.google.com/spreadsheets/d/1mi_QtSfe0SfIv5X22a82Hz6sQrColIre24aZelFyadM/edit#gid=1355164371"

@app.route("/api/scores")
def get_scores():
    now = time.time()
    if now - cache["last_updated"] < 300:
        return jsonify(cache["data"])

    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_SHEET_CREDENTIALS, scope)
        client = gspread.authorize(creds)

        sheet = client.open_by_url(SHEET_URL)
        worksheet = sheet.get_worksheet(0)  # assumes leaderboard is on first tab

        data = worksheet.get_all_values()

        players = {}

        for row in data[1:]:  # skip header
            if len(row) < 2:
                continue

            name = row[0].strip()
            score_raw = row[1].strip()

            if not name or not score_raw:
                continue

            if score_raw == "E":
                score = 0
            else:
                try:
                    score = int(score_raw)
                except:
                    continue

            players[name] = score

        cache["data"] = players
        cache["last_updated"] = now
        return jsonify(players)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# For local dev or Render/Vercel backend
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
