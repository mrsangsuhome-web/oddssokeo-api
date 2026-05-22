from flask import Flask, jsonify
from flask_cors import CORS

import requests
import random
import time
import json
import os

from threading import Thread
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

CORS(app)

API_KEY = os.getenv("PARLAY_API_KEY")

CACHE_FILE = "cache.json"

cached_matches = []

SPORTS = [

    "soccer_epl",

    "soccer_usa_mls",

    "soccer_spain_la_liga",

    "soccer_germany_bundesliga",

    "soccer_italy_serie_a",

    "soccer_france_ligue_one",

    "soccer_portugal_primeira_liga",

    "soccer_netherlands_eredivisie",

    "soccer_turkey_super_lig",

    "soccer_brazil_campeonato",

    "soccer_argentina_primera_division",

    "soccer_japan_j_league",

    "soccer_korea_kleague1",

    "soccer_australia_aleague",

    "soccer_uefa_champs_league",

    "soccer_fifa_world_cup"

]

LEAGUE_MAP = {

    "SOCCER_EPL": "EPL",

    "SOCCER_USA_MLS": "MLS",

    "SOCCER_SPAIN_LA_LIGA": "LAL",

    "SOCCER_GERMANY_BUNDESLIGA": "BUN",

    "SOCCER_ITALY_SERIE_A": "SA",

    "SOCCER_FRANCE_LIGUE_ONE": "L1",

    "SOCCER_PORTUGAL_PRIMEIRA_LIGA": "POR",

    "SOCCER_NETHERLANDS_EREDIVISIE": "NED",

    "SOCCER_TURKEY_SUPER_LIG": "TUR",

    "SOCCER_BRAZIL_CAMPEONATO": "BRA",

    "SOCCER_ARGENTINA_PRIMERA_DIVISION": "ARG",

    "SOCCER_JAPAN_J_LEAGUE": "JPN",

    "SOCCER_KOREA_KLEAGUE1": "KOR",

    "SOCCER_AUSTRALIA_ALEAGUE": "AUS",

    "SOCCER_UEFA_CHAMPS_LEAGUE": "UCL",

    "SOCCER_FIFA_WORLD_CUP": "WC"

}


def generate_live_data():

    status = random.choice([

        "PRE",

        "PRE",

        "PRE",

        "H1",

        "H2",

        "HT"

    ])

    if status == "PRE":

        return {

            "liveStatus": "PRE",

            "minute": None,

            "injury": None

        }

    if status == "HT":

        return {

            "liveStatus": "HT",

            "minute": 45,

            "injury": 0

        }

    minute = random.randint(1, 45)

    injury = random.randint(0, 4)

    return {

        "liveStatus": status,

        "minute": minute,

        "injury": injury

    }


def normalize_bookmaker(name):

    if not name:
        return "BOOK"

    name = name.upper()

    if "PINNACLE" in name:
        return "PIN"

    if "BET365" in name:
        return "365"

    if "188" in name:
        return "188"

    if "SBO" in name:
        return "SBO"

    if "IBC" in name:
        return "IBC"

    if "CMD" in name:
        return "CMD"

    if "SABA" in name:
        return "SABA"

    if "BETINASIA" in name:
        return "BTI"

    if "ISN" in name:
        return "ISN"

    return name[:6]


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

                home_team = game.get(
                    "home_team",
                    "HOME"
                )

                away_team = game.get(
                    "away_team",
                    "AWAY"
                )

                bookmakers = game.get(
                    "bookmakers",
                    []
                )

                real_books = []

                for b in bookmakers:

                    title = b.get("title")

                    if title:

                        real_books.append(
                            normalize_bookmaker(title)
                        )

                if len(real_books) >= 2:

                    bookA, bookB = random.sample(
                        real_books,
                        2
                    )

                else:

                    bookA, bookB = random.sample(
                        [
                            "SBO",
                            "PIN",
                            "IBC",
                            "188",
                            "CMD",
                            "SABA",
                            "BTI",
                            "ISN"
                        ],
                        2
                    )

                base = round(
                    random.uniform(0.84, 0.96),
                    2
                )

                movement = random.choice([

                    -0.02,

                    -0.01,

                    0.01,

                    0.02

                ])

                awayOddA = round(base, 2)

                awayOddB = round(
                    base + movement,
                    2
                )

                homeOddA = round(
                    random.uniform(0.84, 0.96),
                    2
                )

                homeOddB = round(
                    random.uniform(0.84, 0.96),
                    2
                )

                gap = round(
                    abs(
                        awayOddA - awayOddB
                    ),
                    2
                )

                market = random.choice([

                    "FT O/U",

                    "FT HDP"

                ])

                line = random.choice([

                    "0.5",

                    "1",

                    "1.5",

                    "2",

                    "2.5",

                    "2.5/3",

                    "3"

                ])

                liveData = generate_live_data()

                results.append({

                    "match":
                        f"{home_team} vs {away_team}",

                    "league":
                        LEAGUE_MAP.get(
                            SPORT.upper(),
                            SPORT.upper()
                        ),

                    "market":
                        market,

                    "line":
                        line,

                    "bookA":
                        bookA,

                    "bookB":
                        bookB,

                    "awayOddA":
                        awayOddA,

                    "awayOddB":
                        awayOddB,

                    "homeOddA":
                        homeOddA,

                    "homeOddB":
                        homeOddB,

                    "gap":
                        gap,

                    "liveStatus":
                        liveData["liveStatus"],

                    "minute":
                        liveData["minute"],

                    "injury":
                        liveData["injury"],

                    "timestamp":
                        int(time.time())

                })

        results.sort(
            key=lambda x:
                x["timestamp"],
            reverse=True
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


@app.route("/")
def home():

    return jsonify({

        "status": "running",

        "matches": len(cached_matches),

        "source": "PARLAY API"

    })


@app.route("/matches")
def matches():

    return jsonify(
        cached_matches
    )


def background_loop():

    while True:

        fetch_odds()

        time.sleep(8)


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