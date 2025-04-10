from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

@app.route("/api/espn-table")
def get_espn_table():
    try:
        url = "https://www.espn.com/golf/leaderboard"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        res = requests.get(url, headers=headers)
        res.raise_for_status()

        soup = BeautifulSoup(res.text, "html.parser")
        tables = soup.find_all("table")

        if not tables:
            return jsonify({"error": "No tables found"})

        # Convert all tables to a list of row/column values
        parsed_tables = []
        for table in tables:
            rows = []
            for tr in table.find_all("tr"):
                cells = [td.get_text(strip=True) for td in tr.find_all(["th", "td"])]
                if cells:
                    rows.append(cells)
            parsed_tables.append(rows)

        return jsonify({"tables": parsed_tables})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
