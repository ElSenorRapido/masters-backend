from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
from rapidfuzz import process
import os
import time

app = Flask(__name__)

cache = {
    "espn_data": [],
    "scores": {},
    "last_updated": 0
}

initialPlayers = [
    {"name": "J Duerr", "picks": ["Rory McIlroy", "Bryson DeChambeau", "Justin Thomas", "Ludvig Aberg", "Robert Macintyre", "Daniel Berger"], "tiebreaker": "-10"},
    {"name": "Train", "picks": ["Jon Rahm", "Bryson DeChambeau", "Justin Thomas", "Ludvig Aberg", "Wyndham Clark", "J.J. Spaun"], "tiebreaker": "-10"},
    {"name": "Bilitz", "picks": ["Xander Schauffle", "Brooks Koepka", "Tony Finau", "Sam Burns", "Taylor Pendrith", "Zach Johnson"], "tiebreaker": "-12"},
    {"name": "Van Evans", "picks": ["Rory McIlroy", "Brooks Koepka", "Justin Thomas", "Ludvig Aberg", "Billy Horschel", "Lucas Glover"], "tiebreaker": "-15"},
    {"name": "Josh", "picks": ["Rory McIlroy", "Bryson DeChambeau", "Tony Finau", "Max Homa", "Wyndham Clark", "Cameron Davis"], "tiebreaker": "-9"},
    {"name": "Jack", "picks": ["Scottie Scheffler", "Bryson DeChambeau", "Joaquin Niemann", "Ludvig Aberg", "Akshay Bhatia", "J.J. Spaun"], "tiebreaker": "-10"},
    {"name": "BIG JON", "picks": ["Scottie Scheffler", "Bryson DeChambeau", "Tony Finau", "Dustin Johnson", "Justin Rose", "Bubba Watson"], "tiebreaker": "-12"},
    {"name": "Austin", "picks": ["Scottie Scheffler", "Viktor Hovland", "Joaquin Niemann", "Ludvig Aberg", "Billy Horschel", "Cameron Davis"], "tiebreaker": "-12"},
    {"name": "MEEP", "picks": ["Scottie Scheffler", "Bryson DeChambeau", "Joaquin Niemann", "Ludvig Aberg", "Akshay Bhatia", "J.J. Spaun"], "tiebreaker": "-11"},
    {"name": "Chris George", "picks": ["Shane Lowry", "Russell Henley", "Joaquin Niemann", "Ludvig Aberg", "Akshay Bhatia", "Aaron Rai"], "tiebreaker": "-11"},
    {"name": "Magnolia Madness", "picks": ["Scottie Scheffler", "Bryson DeChambeau", "Joaquin Niemann", "Ludvig Aberg", "Justin Rose", "Phil Mickelson"], "tiebreaker": "-10"},
    {"name": "J. Robrahn", "picks": ["Scottie Scheffler", "Brooks Koepka", "Jordan Spieth", "Ludvig Aberg", "Akshay Bhatia", "Phil Mickelson"], "tiebreaker": "-13"},
    {"name": "Stove", "picks": ["Scottie Scheffler", "Bryson DeChambeau", "Will Zalatoris", "Ludvig Aberg", "Akshay Bhatia", "J.J. Spaun"], "tiebreaker": "-11"},
    {"name": "Magedanz", "picks": ["Scottie Scheffler", "Min Woo Lee", "Justin Thomas", "Ludvig Aberg", "Justin Rose", "Lucas Glover"], "tiebreaker": "-11"},
    {"name": "G Weckwerth", "picks": ["Rory McIlroy", "Bryson DeChambeau", "Jordan Spieth", "Jason Day", "Sergio Garcia", "Phil Mickelson"], "tiebreaker": "-9"},
    {"name": "J Dlobik", "picks": ["Scottie Scheffler", "Bryson DeChambeau", "Justin Thomas", "Ludvig Aberg", "Robert Macintyre", "Daniel Berger"], "tiebreaker": "-11"},
    {"name": "Cole Hernikl", "picks": ["Scottie Scheffler", "Bryson DeChambeau", "Will Zalatoris", "Ludvig Aberg", "Wyndham Clark", "Phil Mickelson"], "tiebreaker": "-13"},
    {"name": "K House", "picks": ["Jon Rahm", "Bryson DeChambeau", "Patrick Reed", "Dustin Johnson", "Sergio Garcia", "Phil Mickelson"], "tiebreaker": "-10"},
    {"name": "Mikey Anderson", "picks": ["Scottie Scheffler", "Corey Conners", "Sepp Straka", "Brian Harman", "Akshay Bhatia", "Maverick McNealy"], "tiebreaker": "-13"},
    {"name": "Drew Lockerby", "picks": ["Scottie Scheffler", "Bryson DeChambeau", "Sepp Straka", "Brian Harman", "Akshay Bhatia", "Daniel Berger"], "tiebreaker": "-18"},
    {"name": "Parlay Pete", "picks": ["Rory McIlroy", "Bryson DeChambeau", "Justin Thomas", "Ludvig Aberg", "Robert Macintyre", "Lucas Glover"], "tiebreaker": "-11"},
    {"name": "Palmer", "picks": ["Scottie Scheffler", "Viktor Hovland", "Sahith Theegala", "Ludvig Aberg", "Akshay Bhatia", "J.J. Spaun"], "tiebreaker": "-13"},
    {"name": "Homakawa", "picks": ["Collin Morikawa", "Viktor Hovland", "Jordan Spieth", "Max Homa", "Sergio Garcia", "Cameron Davis"], "tiebreaker": "-13"},
    {"name": "Matt Dwyer", "picks": ["Rory McIlroy", "Russell Henley", "Will Zalatoris", "Dustin Johnson", "Justin Rose", "Phil Mickelson"], "tiebreaker": "-16"},
    {"name": "Rapido", "picks": ["Scottie Scheffler", "Brooks Koepka", "Sungjae Im", "Jason Day", "Chris Kirk", "Cameron Davis"], "tiebreaker": "-11"},
    {"name": "Ryan Ells", "picks": ["Rory McIlroy", "Brooks Koepka", "Sepp Straka", "Ludvig Aberg", "Billy Horschel", "Lucas Glover"], "tiebreaker": "-12"},
    {"name": "Cristof", "picks": ["Scottie Scheffler", "Russell Henley", "Sepp Straka", "Ludvig Aberg", "Robert Macintyre", "J.T. Poston"], "tiebreaker": "-10"},
    {"name": "Bobby B", "picks": ["Scottie Scheffler", "Bryson DeChambeau", "Jordan Spieth", "Ludvig Aberg", "Nicolai Hojgaard", "Cameron Davis"], "tiebreaker": "-13"},
    {"name": "Daggett1", "picks": ["Scottie Scheffler", "Bryson DeChambeau", "Will Zalatoris", "Ludvig Aberg", "Akshay Bhatia", "Lucas Glover"], "tiebreaker": "-14"},
    {"name": "Daggett2", "picks": ["Rory McIlroy", "Russell Henley", "Tony Finau", "Harris English", "Wyndham Clark", "J.J. Spaun"], "tiebreaker": "-14"},
    {"name": "Robert Neal", "picks": ["Scottie Scheffler", "Bryson DeChambeau", "Sepp Straka", "Ludvig Aberg", "Justin Rose", "Danny Willett"], "tiebreaker": "-10"},
    {"name": "Becker", "picks": ["Rory McIlroy", "Min Woo Lee", "Joaquin Niemann", "Sam Burns", "Wyndham Clark", "Nicolas Echavarria"], "tiebreaker": "-14"},
    {"name": "Morikawa", "picks": ["Collin Morikawa", "Russell Henley", "Will Zalatoris", "Max Homa", "Robert Macintyre", "Maverick McNealy"], "tiebreaker": "-13"},
    {"name": "The God Damn Cantlay Wine Mixer!", "picks": ["Rory McIlroy", "Russell Henley", "Justin Thomas", "Keegan Bradley", "Denny McCarthy", "Daniel Berger"], "tiebreaker": "-10"},
    {"name": "Havland Security", "picks": ["Collin Morikawa", "Viktor Hovland", "Sepp Straka", "Ludvig Aberg", "Robert Macintyre", "J.J. Spaun"], "tiebreaker": "-11"},
    {"name": "Rachel", "picks": ["Collin Morikawa", "Bryson DeChambeau", "Tony Finau", "Keegan Bradley", "Justin Rose", "Cameron Davis"], "tiebreaker": "-17"},
    {"name": "Zach", "picks": ["Scottie Scheffler", "Brooks Koepka", "Adam Scott", "Ludvig Aberg", "Robert Macintyre", "Bubba Watson"], "tiebreaker": "-16"}
]


def fetch_espn_table():
    try:
        res = requests.get("https://www.espn.com/golf/leaderboard", headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        tables = soup.find_all("table")
        for table in tables:
            rows = []
            for tr in table.find_all("tr"):
                cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
                if cells:
                    rows.append(cells)
            if rows and "PLAYER" in rows[0]:
                return rows
    except Exception as e:
        print("ESPN fetch error:", e)
    return []

def parse_espn_scores(table):
    scores = {}
    for row in table[1:]:
        if len(row) >= 4:
            name = row[2]
            raw_score = row[3]
            try:
                score = 0 if raw_score == "E" else int(raw_score)
            except:
                score = 999
            scores[name] = score
    return scores

def get_best_match(name, candidates):
    match, _ = process.extractOne(name, candidates)
    return match

def calculate_score(picks, scores):
    matched_scores = []
    names = list(scores.keys())
    for name in picks:
        matched_name = get_best_match(name, names)
        matched_scores.append(scores.get(matched_name, 999))
    matched_scores.sort()
    return sum(matched_scores[:5])

@app.route("/api/scores")
def get_scores():
    try:
        now = time.time()
        if now - cache["last_updated"] < 300:
            return jsonify(cache["scores"])

        table = fetch_espn_table()
        scores = parse_espn_scores(table)

        leaderboard = []
        for entry in initialPlayers:
            total = calculate_score(entry["picks"], scores)
            leaderboard.append({**entry, "total": total})

        leaderboard.sort(key=lambda x: x["total"])
        cache["scores"] = leaderboard
        cache["last_updated"] = now

        return jsonify(leaderboard)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
