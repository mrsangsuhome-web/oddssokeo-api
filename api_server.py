
from flask import Flask, jsonify
from flask_cors import CORS

import requests
import random
import time
import json
import os

from threading import Thread
from dotenv import load_dotenv
from datetime import datetime, timezone

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

BOOKMAKER_MAP = {

    "PINNACLE": "PIN",
    "BET365": "365",
    "188BET": "188",
    "SBOBET": "SBO",
    "IBCBET": "IBC",
    "CMD368": "CMD",
    "SABA SPORTS": "SABA",
    "BETINASIA": "BTI",
    "ISN": "ISN",
    "MAXBET": "MAX",
    "CROWN": "CRN",
    "M8BET": "M8",
    "1XBET": "1X",
    "BETFAIR": "BFA",
    "MELBET": "MLB",
    "FUN88": "FUN",
    "WILLIAM HILL": "WH",
    "UNIBET": "UNI",
    "10BET": "10B",
    "BETWAY": "BTW",
    "DAFABET": "DFB"

}


def normalize_bookmaker(name):

    if not name:
        return None

    upper_name = name.upper()

    for key, short in BOOKMAKER_MAP.items():

        if key in upper_name:

            return short

    return upper_name[:6]


def generate_live_data(commence_time):

    try:

        match_time = datetime.fromisoformat(
            commence_time.replace("Z", "+00:00")
        )

        now = datetime.now(timezone.utc)

        diff = int(
            (
                now - match_time
            ).total_seconds() / 60
        )

        if diff < -5:

            local_time = match_time.astimezone()

            return {

                "liveStatus": "PRE",

                "displayTime":
                    local_time.strftime("%d/%m • %H:%M"),

                "minute": None,

                "injury": None

            }

        if diff <= 45:

            return {

                "liveStatus": "H1",

                "displayTime": None,

                "minute": diff,

                "injury": random.randint(0, 4)

            }

        if diff <= 60:

            return {

                "liveStatus": "HT",

                "displayTime": None,

                "minute": 45,

                "injury": 0

            }

        if diff <= 110:

            return {

                "liveStatus": "H2",

                "displayTime": None,

                "minute": diff - 15,

                "injury": random.randint(0, 5)

            }

        return {

            "liveStatus": "FIN",

            "displayTime": None,

            "minute": 90,

            "injury": 0

        }

    except:

        return {

            "liveStatus": "PRE",

            "displayTime": "--:--",

            "minute": None,

            "injury": None

        }


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

            print("SPORT:", SPORT)
            print("TOTAL:", len(data))

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

                bookmakers = game.get(
                    "bookmakers",
                    []
                )

                real_books = []

                for b in bookmakers:

                    title = b.get("title")

                    normalized = normalize_bookmaker(title)

                    if normalized:

                        real_books.append(
                            normalized
                        )

                real_books = list(
                    set(real_books)
                )

                if len(real_books) >= 2:

                    bookA, bookB = random.sample(
                        real_books,
                        2
                    )

                elif len(real_books) == 1:

                    bookA = real_books[0]
                    bookB = real_books[0]

                
                else:

                   bookA, bookB = random.sample(
                   DEFAULT_BOOKMAKERS,
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

                liveData = generate_live_data(
                    commence_time
                )

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

                    "displayTime":
                        liveData["displayTime"],

                    "minute":
                        liveData["minute"],

                    "injury":
                        liveData["injury"],

                    "timestamp":
                        int(time.time())

                })

        cached_matches = sorted(

            results,

            key=lambda x:
                x["timestamp"],

            reverse=True

        )[:20]

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

            print("USING CACHE DATA")


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

