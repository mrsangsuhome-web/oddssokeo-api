import requests
import time
import json
import os

from flask import Flask, jsonify
from flask_cors import CORS
from threading import Thread

app = Flask(__name__)
CORS(app)

API_KEY = "6073d49f9663c2f28a4b82dc1dfb002d"

SPORTS = [
    "soccer_epl",
    "soccer_usa_mls",
    "soccer_spain_la_liga",
    "soccer_germany_bundesliga",
    "soccer_brazil_campeonato"
]

CACHE_FILE = "cache.json"

cached_matches = []

def fetch_odds():

    global cached_matches

    results = []

    try:

        for SPORT in SPORTS:

            url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds"

            params = {
                "apiKey": API_KEY,
                "regions": "eu",
                "markets": "spreads",
                "oddsFormat": "decimal"
            }

            response = requests.get(
                url,
                params=params,
                timeout=20
            )

            data = response.json()

            if not isinstance(data, list):
                continue

            for game in data:

                home_team = game.get(
                    "home_team",
                    "HOME"
                )

                away_team = game.get(
                    "away_team",
                    "AWAY"
                )

                commence_time = game.get(
                    "commence_time",
                    ""
                )

                results.append({

                    "match":
                        f"{home_team} vs {away_team}",

                    "league":
                        SPORT
                        .replace(
                            "soccer_",
                            ""
                        )
                        .upper(),

                    "commence_time":
                        commence_time,

                    "curr_odds":
                        "0.88",

                    "curr_ah":
                        "2.5"

                })

        if len(results) == 0:

            raise Exception(
                "NO MATCHES FROM API"
            )

        cached_matches = results[:20]

        with open(
            CACHE_FILE,
            "w"
        ) as f:

            json.dump(
                cached_matches,
                f
            )

        print(
            f"UPDATED {len(cached_matches)} MATCHES"
        )

    except Exception as e:

        print("API ERROR:", e)

        if os.path.exists(
            CACHE_FILE
        ):

            with open(
                CACHE_FILE,
                "r"
            ) as f:

                cached_matches = json.load(f)

            print(
                "USING CACHE DATA"
            )

        else:

            cached_matches = [

                {
                    "match":
                        "Chelsea vs Arsenal",

                    "league":
                        "EPL",

                    "commence_time":
                        "2026-05-20T19:00:00Z",

                    "curr_odds":
                        "0.88",

                    "curr_ah":
                        "2.5"
                },

                {
                    "match":
                        "Barcelona vs Real Madrid",

                    "league":
                        "LA LIGA",

                    "commence_time":
                        "2026-05-21T20:00:00Z",

                    "curr_odds":
                        "0.90",

                    "curr_ah":
                        "0.5"
                }

            ]

@app.route("/")

def home():

    return jsonify({

        "status":
            "running",

        "matches":
            len(cached_matches)

    })

@app.route("/matches")

def matches():

    return jsonify(cached_matches)

def background_loop():

    while True:

        fetch_odds()

        time.sleep(1600)

if __name__ == "__main__":

    fetch_odds()

    Thread(
        target=background_loop,
        daemon=True
    ).start()

    app.run(
        host="0.0.0.0",
        port=10000
    )

