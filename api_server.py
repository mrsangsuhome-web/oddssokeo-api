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

    "soccer_uefa_europa_league",

    "soccer_spain_la_liga",

    "soccer_spain_segunda_division",

    "soccer_italy_serie_a",

    "soccer_italy_serie_b",

    "soccer_germany_bundesliga",

    "soccer_germany_bundesliga2",

    "soccer_france_ligue_one",

    "soccer_france_ligue_two",

    "soccer_netherlands_eredivisie",

    "soccer_portugal_primeira_liga",

    "soccer_turkey_super_league",

    "soccer_belgium_first_div",

    "soccer_sweden_allsvenskan",

    "soccer_norway_eliteserien",

    "soccer_denmark_superliga",

    "soccer_brazil_campeonato",

    "soccer_argentina_primera_division",

    "soccer_usa_mls",

    "soccer_mexico_ligamx",

    "soccer_japan_j_league",

    "soccer_korea_kleague1",

    "soccer_china_superleague",

    "soccer_australia_aleague"


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

def generate_fake_gap(price):

    drift = round(

        random.uniform(
            -0.03,
            0.03
        ),

        2

    )

    value = round(
        price + drift,
        2
    )

    if value < 0.80:
        value = 0.80

    if value > 0.99:
        value = 0.99

    return value

def build_market(

    bookA,
    bookB,
    league,
    match,
    commence_time

):

    oddA1 = round(

        random.uniform(
            0.86,
            0.94
        ),

        2

    )

    oddA2 = round(
        1.80 - oddA1,
        2
    )

    oddB1 = generate_fake_gap(
        oddA1
    )

    oddB2 = round(
        1.80 - oddB1,
        2
    )

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

    market_type = random.choice([
        "FT HDP",
        "FT O/U"
    ])

    line = random.choice([

        "0",

        "0/0.5",

        "0.5",

        "1",

        "1.5",

        "2",

        "2.5",

        "2.5/3"

    ])

    return {

    "match":
        match,

    "league":
        league,

    "market":
        market_type,

    "line":
        line,

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
        commence_time,

    "live":
        random.choice([
            True,
            False
        ]),

    "liveTime":
        random.choice([

            "H1 4'",

            "H1 15'",

            "H1 28'",

            "H1 45+2'",

            "HT",

            "H2 51'",

            "H2 67'",

            "H2 79'",

            "H2 90+2'"

        ])

}

def fetch_odds():

    global cached_matches
    global bookmaker_stats

    results = []

    book_counter = Counter()

    try:

        headers = {

            "X-API-Key":
                API_KEY

        }

        for sport in SPORTS:

            url = (
                "https://parlay-api.com"
                f"/v1/sports/{sport}/events"
            )

            response = requests.get(

                url,

                headers=headers,

                timeout=20

            )

            print(
                "SPORT:",
                sport,
                "STATUS:",
                response.status_code
            )

            if response.status_code != 200:

                print(
                    response.text
                )

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

                books = [

                    "PIN",

                    "SBO",

                    "IBC",

                    "188",

                    "CMD",

                    "BTI",

                    "SABA",

                    "KSP"

                ]

                for i in range(2):

                    bookA = random.choice(
                        books
                    )

                    bookB = random.choice(
                        books
                    )

                    while bookA == bookB:

                        bookB = random.choice(
                            books
                        )

                    parsed = build_market(

                        bookA,

                        bookB,

                        sport
                        .replace(
                            "soccer_",
                            ""
                        )
                        .upper(),

                        match,

                        commence_time

                    )

                    results.append(
                        parsed
                    )

                    book_counter[
                        bookA
                    ] += 1

                    book_counter[
                        bookB
                    ] += 1

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

        if os.path.exists(
            CACHE_FILE
        ):

            with open(
                CACHE_FILE,
                "r"
            ) as f:

                cache = json.load(
                    f
                )

                cached_matches = cache.get(
                    "matches",
                    []
                )

                bookmaker_stats = cache.get(
                    "books",
                    []
                )

                print(
                    "USING CACHE DATA"
                )

@app.route("/")

def home():

    return jsonify({

        "status":
            "running",

        "matches":
            len(
                cached_matches
            ),

        "bookmakers":
            len(
                bookmaker_stats
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