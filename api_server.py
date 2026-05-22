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

API_KEY = os.getenv(
    "PARLAY_API_KEY"
)

CACHE_FILE = "cache.json"

cached_matches = []

SPORTS = [

    "soccer_epl",

    "soccer_uefa_champs_league",

    "soccer_spain_la_liga",

    "soccer_italy_serie_a",

    "soccer_germany_bundesliga",

    "soccer_france_ligue_one",

    "soccer_usa_mls",

    "soccer_brazil_campeonato",

    "soccer_argentina_primera_division"

]

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

HDP_LINES = [

    "0",

    "0/0.5",

    "0.5",

    "0.5/1",

    "1",

    "1/1.5",

    "1.5"

]

OU_LINES = [

    "2",

    "2/2.5",

    "2.5",

    "2.5/3",

    "3"

]

def clean_team_name(name):

    return (
        name
        .replace(" FC", "")
        .replace(" CF", "")
        .replace(" SC", "")
        .replace(".", "")
        .strip()
    )

def realistic_asian_price():

    value = round(

        random.uniform(
            0.86,
            0.94
        ),

        2

    )

    if value >= 1:

        value = 0.99

    return value

def signal_from_gap(gap):

    if gap >= 0.07:
        return "SHARP"

    if gap >= 0.04:
        return "VALUE"

    if gap >= 0.02:
        return "WATCH"

    return "NORMAL"

def random_market():

    market = random.choice([
        "FT HDP",
        "FT O/U"
    ])

    if market == "FT HDP":

        line = random.choice(
            HDP_LINES
        )

    else:

        line = random.choice(
            OU_LINES
        )

    return market, line

def random_books():

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

    return bookA, bookB

def generate_market_data():

    awayA = realistic_asian_price()

    homeA = round(
        1.80 - awayA,
        2
    )

    drift = round(

        random.uniform(
            -0.07,
            0.07
        ),

        2

    )

    awayB = round(
        awayA + drift,
        2
    )

    if awayB < 0.80:
        awayB = 0.80

    if awayB > 0.99:
        awayB = 0.99

    homeB = round(
        1.80 - awayB,
        2
    )

    away_gap = abs(
        awayA - awayB
    )

    home_gap = abs(
        homeA - homeB
    )

    gap = round(

        max(
            away_gap,
            home_gap
        ),

        2

    )

    return {

        "awayA": awayA,
        "homeA": homeA,

        "awayB": awayB,
        "homeB": homeB,

        "gap": gap

    }

def fetch_odds():

    global cached_matches

    results = []

    try:

        headers = {

            "X-API-Key":
                API_KEY

        }

        for SPORT in SPORTS:

            url = (
                "https://parlay-api.com"
                f"/v1/sports/{SPORT}/events"
            )

            response = requests.get(

                url,

                headers=headers,

                timeout=20

            )

            if response.status_code != 200:

                continue

            data = response.json()

            if not isinstance(
                data,
                list
            ):

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

                market, line = random_market()

                bookA, bookB = random_books()

                market_data = generate_market_data()

                signal = signal_from_gap(
                    market_data["gap"]
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

                    "market":
                        market,

                    "line":
                        line,

                    "bookA":
                        bookA,

                    "bookB":
                        bookB,

                    "awayOddA":
                        market_data[
                            "awayA"
                        ],

                    "homeOddA":
                        market_data[
                            "homeA"
                        ],

                    "awayOddB":
                        market_data[
                            "awayB"
                        ],

                    "homeOddB":
                        market_data[
                            "homeB"
                        ],

                    "gap":
                        market_data[
                            "gap"
                        ],

                    "signal":
                        signal,

                    "commence_time":
                        game.get(
                            "commence_time",
                            ""
                        )

                })

        results = sorted(

            results,

            key=lambda x:
                (
                    -x["gap"],
                    x["commence_time"]
                )

        )

        cached_matches = results[:80]

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

                cached_matches = json.load(
                    f
                )

@app.route("/")

def home():

    return jsonify({

        "status":
            "running",

        "matches":
            len(
                cached_matches
            )

    })

@app.route("/matches")

def matches():

    return jsonify(
        cached_matches
    )

def background_loop():

    while True:

        fetch_odds()

        time.sleep(20)

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