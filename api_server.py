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

    "soccer_italy_serie_a"

]

CACHE_FILE = "cache.json"

cached_matches = []

BOOKMAKERS = [

    "Pinnacle",

    "Bet365",

    "188Bet",

    "SBOBet",

    "CMD368",

    "IBCBet",

    "ISN",

    "BTI",

    "SABA",

    "KSport"

]

LINES = [

    "0",

    "0/0.5",

    "0.5",

    "0.5/1",

    "1",

    "1/1.5",

    "1.5",

    "2",

    "2.5"

]

def clean_team_name(name):

    return (
        name
        .replace(" FC", "")
        .replace(" SC", "")
        .replace(" CF", "")
        .replace(".", "")
        .strip()
    )

def asian_price():

    return round(

        random.choice([

            0.82,
            0.84,
            0.86,
            0.88,
            0.90,
            0.92,
            0.94,
            0.96,
            0.98

        ]),

        2

    )

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
                continue

            data = response.json()

            if not isinstance(data, list):
                continue

            for game in data:

                home_team = clean_team_name(
                    game.get(
                        "home_team",
                        "HOME"
                    )
                )

                away_team = clean_team_name(
                    game.get(
                        "away_team",
                        "AWAY"
                    )
                )

                line = random.choice(
                    LINES
                )

                bookA = random.choice(
                    BOOKMAKERS
                )

                bookB = random.choice(
                    BOOKMAKERS
                )

                while bookA == bookB:

                    bookB = random.choice(
                        BOOKMAKERS
                    )

                awayA = asian_price()
                homeA = asian_price()

                awayB = asian_price()
                homeB = asian_price()

                gap = round(

                    max(

                        abs(
                            awayA - awayB
                        ),

                        abs(
                            homeA - homeB
                        )

                    ),

                    2

                )

                signal = "NORMAL"

                if gap >= 0.12:

                    signal = "VALUE"

                if gap >= 0.18:

                    signal = "SHARP"

                results.append({

                    "match":
                        f"{home_team} vs {away_team}",

                    "market":
                        "FT HDP",

                    "line":
                        line,

                    "bookA":
                        bookA,

                    "bookB":
                        bookB,

                    "awayOddA":
                        awayA,

                    "homeOddA":
                        homeA,

                    "awayOddB":
                        awayB,

                    "homeOddB":
                        homeB,

                    "gap":
                        gap,

                    "signal":
                        signal,

                    "commence_time":
                        game.get(
                            "commence_time",
                            ""
                        )

                })

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

    return jsonify(
        cached_matches
    )

def background_loop():

    while True:

        fetch_odds()

        time.sleep(60)

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