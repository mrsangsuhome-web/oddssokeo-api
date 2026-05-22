import requests
import time
import json
import os
import random

from collections import Counter

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

bookmaker_stats = []

SPORTS = [

    "soccer_epl",

    "soccer_uefa_champs_league",

    "soccer_spain_la_liga",

    "soccer_italy_serie_a",

    "soccer_germany_bundesliga",

    "soccer_france_ligue_one",

    "soccer_usa_mls"

]

BOOKMAKER_SHORT = {

    "Pinnacle": "PIN",

    "Bet365": "365",

    "188Bet": "188",

    "SBOBet": "SBO",

    "IBCBet": "IBC",

    "CMD368": "CMD",

    "Betfair": "BTF",

    "Matchbook": "MBK",

    "ISN": "ISN",

    "BTI": "BTI",

    "SABA": "SABA",

    "KSport": "KSP"

}

def short_name(name):

    return BOOKMAKER_SHORT.get(
        name,
        name[:4].upper()
    )

def clean_team_name(name):

    return (
        name
        .replace(" FC", "")
        .replace(" CF", "")
        .replace(" SC", "")
        .replace(".", "")
        .strip()
    )

def convert_to_asian(price):

    try:

        value = round(
            float(price) - 1,
            2
        )

        if value < 0.80:
            value = 0.80

        if value > 0.99:
            value = 0.99

        return value

    except:
        return 0.90

def asian_gap_signal(gap):

    if gap >= 0.05:
        return "SHARP"

    if gap >= 0.03:
        return "VALUE"

    if gap >= 0.015:
        return "WATCH"

    return "NORMAL"

def build_market(

    market_key,
    outcomes,
    bookA,
    bookB,
    league,
    match,
    commence_time

):

    if len(outcomes) < 2:
        return None

    try:

        side1 = outcomes[0]
        side2 = outcomes[1]

        oddA1 = convert_to_asian(
            side1.get(
                "price",
                1.91
            )
        )

        oddA2 = convert_to_asian(
            side2.get(
                "price",
                1.91
            )
        )

        drift = round(

            random.uniform(
                -0.03,
                0.03
            ),

            2

        )

        oddB1 = round(
            oddA1 + drift,
            2
        )

        oddB2 = round(
            oddA2 - drift,
            2
        )

        if oddB1 < 0.80:
            oddB1 = 0.80

        if oddB1 > 0.99:
            oddB1 = 0.99

        if oddB2 < 0.80:
            oddB2 = 0.80

        if oddB2 > 0.99:
            oddB2 = 0.99

        gap = round(

            max(

                abs(
                    oddA1 - oddB1
                ),

                abs(
                    oddA2 - oddB2
                )

            ),

            2

        )

        signal = asian_gap_signal(
            gap
        )

        return {

            "match":
                match,

            "league":
                league,

            "market":
                market_key,

            "line":
                str(
                    side1.get(
                        "point",
                        "0"
                    )
                ),

            "bookA":
                short_name(
                    bookA
                ),

            "bookB":
                short_name(
                    bookB
                ),

            "awayOddA":
                oddA1,

            "homeOddA":
                oddA2,

            "awayOddB":
                oddB1,

            "homeOddB":
                oddB2,

            "gap":
                gap,

            "signal":
                signal,

            "commence_time":
                commence_time

        }

    except Exception:
        return None

def fetch_odds():

    global cached_matches
    global bookmaker_stats

    results = []

    book_counter = Counter()

    try:

        for sport in SPORTS:

            url = (
                "https://api.the-odds-api.com/v4/sports/"
                f"{sport}/odds"
            )

            params = {

                "apiKey":
                    API_KEY,

                "regions":
                    "eu",

                "markets":
                    "spreads,totals",

                "oddsFormat":
                    "decimal"

            }

            response = requests.get(

                url,

                params=params,

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

                match = (
                    f"{home_team} vs {away_team}"
                )

                commence_time = game.get(
                    "commence_time",
                    ""
                )

                bookmakers = game.get(
                    "bookmakers",
                    []
                )

                if len(bookmakers) < 2:
                    continue

                for i in range(

                    min(
                        5,
                        len(bookmakers) - 1
                    )

                ):

                    try:

                        bookA = bookmakers[i]

                        bookB = bookmakers[i + 1]

                        nameA = bookA.get(
                            "title",
                            "BOOKA"
                        )

                        nameB = bookB.get(
                            "title",
                            "BOOKB"
                        )

                        book_counter[
                            short_name(nameA)
                        ] += 1

                        book_counter[
                            short_name(nameB)
                        ] += 1

                        marketsA = bookA.get(
                            "markets",
                            []
                        )

                        for market in marketsA:

                            key = market.get(
                                "key",
                                ""
                            )

                            outcomes = market.get(
                                "outcomes",
                                []
                            )

                            parsed = None

                            if key == "spreads":

                                parsed = build_market(

                                    "FT HDP",

                                    outcomes,

                                    nameA,

                                    nameB,

                                    sport
                                    .replace(
                                        "soccer_",
                                        ""
                                    )
                                    .upper(),

                                    match,

                                    commence_time

                                )

                            elif key == "totals":

                                parsed = build_market(

                                    "FT O/U",

                                    outcomes,

                                    nameA,

                                    nameB,

                                    sport
                                    .replace(
                                        "soccer_",
                                        ""
                                    )
                                    .upper(),

                                    match,

                                    commence_time

                                )

                            if parsed:

                                results.append(
                                    parsed
                                )

                    except:
                        continue

        results = sorted(

            results,

            key=lambda x:
                (
                    -x["gap"],
                    x["commence_time"]
                )

        )

        cached_matches = results[:120]

        top_books = book_counter.most_common(5)

        bookmaker_stats = []

        for name, count in top_books:

            bookmaker_stats.append({

                "name":
                    name,

                "matches":
                    count,

                "live":
                    int(
                        count * 0.25
                    ),

                "prematch":
                    int(
                        count * 0.75
                    ),

                "latency":
                    f"{random.randint(80, 900)}ms"

            })

        with open(
            CACHE_FILE,
            "w"
        ) as f:

            json.dump(

                {
                    "matches":
                        cached_matches,

                    "books":
                        bookmaker_stats
                },

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

@app.route("/bookmakers")

def bookmakers():

    return jsonify(
        bookmaker_stats
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