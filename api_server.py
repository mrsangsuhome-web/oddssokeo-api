from flask import Flask, jsonify
from flask_cors import CORS

import requests
import time

app = Flask(__name__)

CORS(app)

API_KEY = "4e33248024942ca4651ab2f6d806c05d"

CACHE = []

LAST_UPDATE = 0

UPDATE_INTERVAL = 180

@app.route("/")

def home():

    return {

        "status":
            "scanner online"

    }

@app.route("/matches")

def matches():

    global CACHE
    global LAST_UPDATE

    now = time.time()

    if (
        now - LAST_UPDATE
        < UPDATE_INTERVAL
    ):

        return jsonify(CACHE)

    url = (

        f"https://api.the-odds-api.com/v4/sports/"
        f"soccer_epl/odds/?apiKey={API_KEY}"
        f"&regions=eu"
        f"&markets=spreads,totals"

    )

    response = requests.get(
        url,
        timeout=20
    )

    data = response.json()

    results = []

    for match in data:

        try:

            bookmakers = (
                match.get(
                    "bookmakers",
                    []
                )
            )

            if not bookmakers:
                continue

            first_book = (
                bookmakers[0]
            )

            markets = (
                first_book.get(
                    "markets",
                    []
                )
            )

            if not markets:
                continue

            first_market = (
                markets[0]
            )

            outcomes = (
                first_market.get(
                    "outcomes",
                    []
                )
            )

            if len(outcomes) < 2:
                continue

            results.append({

                "match":
                    f"{match['home_team']} vs {match['away_team']}",

                "league":
                    "EPL",

                "commence_time":
                    match.get(
                        "commence_time",
                        "-"
                    ),

                "curr_ah":
                    str(
                        outcomes[0].get(
                            "point",
                            "-"
                        )
                    ),

                "curr_odds":
                    str(
                        outcomes[0].get(
                            "price",
                            "-"
                        )
                    ),

                "pi":
                    "+0.08"

            })

        except Exception as e:

            print(e)

    CACHE = results

    LAST_UPDATE = now

    return jsonify(CACHE)

app.run(
    host="0.0.0.0",
    port=10000
)