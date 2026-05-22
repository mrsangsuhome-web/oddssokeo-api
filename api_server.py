
import requests
import time
import json
import os
import random

from flask import Flask, jsonify
from flask_cors import CORS
from threading import Thread

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

API_KEY = os.getenv("PARLAY_API_KEY")

SPORTS = [

    "soccer_epl",

    "soccer_usa_mls",

    "soccer_spain_la_liga",

    "soccer_germany_bundesliga",

    "soccer_italy_serie_a"

]

CACHE_FILE = "cache.json"

cached_matches = []

def fetch_odds():

    global cached_matches

    results = []

    try:

        headers = {
            "X-API-Key": API_KEY
        }

        for SPORT in SPORTS:

            url = (
                f"https://parlay-api.com/v1/"
                f"sports/{SPORT}/events"
            )

            response = requests.get(
                url,
                headers=headers,
                timeout=20
            )

            if response.status_code != 200:

                print(
                    f"API FAILED {SPORT}",
                    response.status_code
                )

                continue

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

                curr_ah = random.choice([

                    "0",
                    "0/0.5",
                    "0.5",
                    "0.5/1",
                    "1",
                    "2",
                    "2.5",
                    "2.5/3"

                ])

                curr_odds = str(

                    round(

                        random.uniform(
                            -0.92,
                            0.92
                        ),

                        2

                    )

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
                        curr_odds,

                    "curr_ah":
                        curr_ah

                })

        if len(results) == 0:

            raise Exception(
                "NO MATCHES FROM API"
            )

        results.sort(
            key=lambda x:
                x["commence_time"]
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

        print(
            "API ERROR:",
            e
        )

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
                        "Liverpool vs Arsenal",

                    "league":
                        "EPL",

                    "commence_time":
                        "2026-05-24T15:00:00Z",

                    "curr_odds":
                        "0.42",

                    "curr_ah":
                        "2.5"
                }

            ]

@app.route("/")

def home():

    return jsonify({

        "status":
            "running",

        "matches":
            len(cached_matches),

        "source":
            "PARLAY API"

    })

@app.route("/matches")

def matches():

    return jsonify(
        cached_matches
    )

def background_loop():

    while True:

        fetch_odds()

        time.sleep(180)

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

