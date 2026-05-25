
from flask import Flask, jsonify
from flask_cors import CORS

import requests
import time
import json
import os
import random

from threading import Thread
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)

CORS(app)

API_KEY = os.getenv("PARLAY_API_KEY")

CACHE_FILE = "cache.json"

cached_matches = []

console_logs = []

movement_history = {}

heatmap_cache = []

live_events_cache = []

SPORTS = [

    "soccer_epl",
    "soccer_england_championship",
    "soccer_spain_la_liga",
    "soccer_germany_bundesliga",
    "soccer_italy_serie_a",
    "soccer_france_ligue_one",
    "soccer_usa_mls",
    "soccer_japan_j_league",
    "soccer_korea_kleague1",
    "soccer_china_superleague",
    "soccer_netherlands_eredivisie",
    "soccer_belgium_first_div",
    "soccer_uefa_champs_league",

    "soccer_australia_npl_queensland",
    "soccer_australia_npl_victoria",
    "soccer_australia_npl_tasmania",

    "soccer_ofc_pro_league"

]

BOOKMAKER_MAP = {

    "PINNACLE": "PIN",
    "BET365": "365",
    "188BET": "188",
    "SBOBET": "SBO",
    "IBCBET": "IBC",
    "CMD368": "CMD",
    "SABA SPORTS": "SABA",
    "BETINASIA": "BTI"

}

DEFAULT_BOOKS = [

    "PIN",
    "365",
    "188",
    "SBO",
    "IBC",
    "CMD",
    "SABA",
    "BTI"

]

LEAGUE_NAMES = {

    "soccer_epl":
        {
            "short": "EPL",
            "name": "England Premier League"
        },

    "soccer_spain_la_liga":
        {
            "short": "LAL",
            "name": "Spain La Liga"
        },

    "soccer_germany_bundesliga":
        {
            "short": "BUN",
            "name": "Germany Bundesliga"
        },

    "soccer_italy_serie_a":
        {
            "short": "SA",
            "name": "Italy Serie A"
        },

    "soccer_france_ligue_one":
        {
            "short": "L1",
            "name": "France Ligue 1"
        },

    "soccer_usa_mls":
        {
            "short": "MLS",
            "name": "USA Major League Soccer"
        },

    "soccer_japan_j_league":
        {
            "short": "J1",
            "name": "Japan J1 League"
        },

    "soccer_korea_kleague1":
        {
            "short": "K1",
            "name": "Korea K League 1"
        },

    "soccer_netherlands_eredivisie":
        {
            "short": "NED",
            "name": "Netherlands Eredivisie"
        },

    "soccer_belgium_first_div":
        {
            "short": "BEL",
            "name": "Belgium First Division"
        },

    "soccer_uefa_champs_league":
        {
            "short": "UCL",
            "name": "UEFA Champions League"
        }

}


def normalize_bookmaker(name):

    if not name:
        return None

    upper_name = str(name).upper()

    for key, short in BOOKMAKER_MAP.items():

        if key in upper_name:
            return short

    return upper_name[:6]


def parse_live_data(game):

    completed = game.get(
        "completed",
        False
    )

    commence_time = game.get(
        "commence_time",
        ""
    )

    scores = game.get(
        "scores",
        []
    )

    home_score = 0
    away_score = 0

    try:

        if isinstance(scores, list):

            if len(scores) >= 2:

                home_score = int(
                    scores[0].get(
                        "score",
                        0
                    )
                )

                away_score = int(
                    scores[1].get(
                        "score",
                        0
                    )
                )

    except:
        pass

    try:

        match_time = datetime.fromisoformat(
            commence_time.replace(
                "Z",
                "+00:00"
            )
        )

        now = datetime.utcnow().replace(
            tzinfo=match_time.tzinfo
        )

        if completed:

            return {

                "status": "FIN",

                "clock": "FT",

                "displayTime": None,

                "homeScore": home_score,

                "awayScore": away_score

            }

        if match_time <= now:

            minutes_live = int(
                (
                    now - match_time
                ).total_seconds() / 60
            )

            if minutes_live <= 45:

                display_clock = f"{minutes_live}'"

            elif minutes_live <= 60:

                display_clock = "HT"

            elif minutes_live <= 105:

                second_half = minutes_live - 15

                display_clock = f"{second_half}'"

            else:

                display_clock = "90+'"

            return {

                "status": "LIVE",

                "clock": display_clock,

                "displayTime": None,

                "homeScore": home_score,

                "awayScore": away_score

            }

        return {

            "status": "PRE",

            "clock": None,

            "displayTime":
                match_time.strftime(
                    "%d/%m • %H:%M"
                ),

            "homeScore": None,

            "awayScore": None

        }

    except:

        return {

            "status": "PRE",

            "clock": None,

            "displayTime": "--/-- • --:--",

            "homeScore": None,

            "awayScore": None

        }


def fetch_matches():

    global cached_matches

    results = []

    seen_matches = set()

    try:

        headers = {
            "X-API-Key": API_KEY
        }

        for sport in SPORTS:

            try:

                url = (
                    f"https://parlay-api.com/v1/"
                    f"sports/{sport}/events"
                )

                response = requests.get(
                    url,
                    headers=headers,
                    timeout=15
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

                    match_name = (
                        f"{home_team} vs {away_team}"
                    )

                    lower_match = match_name.lower()

                    banned_keywords = [

                        "(bookings)",
                        "booking",
                        "(corners)",
                        "corner",
                        "(cards)",
                        "card"

                    ]

                    should_skip = False

                    for keyword in banned_keywords:

                        if keyword in lower_match:

                            should_skip = True
                            break

                    if should_skip:
                        continue

                    normalized_match = (
                        match_name
                        .replace("United", "Utd")
                        .replace("Wolverhampton", "Wolves")
                        .strip()
                        .lower()
                    )

                    if normalized_match in seen_matches:
                        continue

                    seen_matches.add(
                        normalized_match
                    )

                    bookmakers = game.get(
                        "bookmakers",
                        []
                    )

                    real_books = []

                    for b in bookmakers:

                        normalized = normalize_bookmaker(
                            b.get("title")
                        )

                        if normalized:
                            real_books.append(
                                normalized
                            )

                    real_books = list(
                        set(real_books)
                    )

                    if len(real_books) >= 2:

                        bookA = real_books[0]
                        bookB = real_books[1]

                    else:

                        bookA, bookB = random.sample(
                            DEFAULT_BOOKS,
                            2
                        )

                    live_data = parse_live_data(
                        game
                    )

                    results.append({

                        "match": match_name,

                        "league":
                            LEAGUE_NAMES.get(
                                sport,
                                {}
                            ).get(
                                "short",
                                sport.upper()
                            ),

                        "leagueName":
                            LEAGUE_NAMES.get(
                                sport,
                                {}
                            ).get(
                                "name",
                                sport.upper()
                            ),

                        "market": "FT O/U",

                        "periodMarket": "FT",

                        "line": "2.5",

                        "bookA": bookA,
                        "bookB": bookB,

                        "awayOddA": 0.91,
                        "awayOddB": 0.93,

                        "homeOddA": 0.89,
                        "homeOddB": 0.87,

                        "gap": 0.02,

                        "movementDelta": 0.02,

                        "heatLevel": "NORMAL",

                        "liveStatus":
                            live_data["status"],

                        "clock":
                            live_data["clock"],

                        "displayTime":
                            live_data["displayTime"],

                        "homeScore":
                            live_data["homeScore"],

                        "awayScore":
                            live_data["awayScore"],

                        "timestamp":
                            int(time.time())

                    })

            except Exception as e:

                print(
                    "SPORT ERROR",
                    sport,
                    e
                )

        results = sorted(

            results,

            key=lambda x: (

                x["liveStatus"] != "LIVE",

                -x["timestamp"]

            )

        )

        cached_matches = results[:150]

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
            "FETCH ERROR",
            e
        )


@app.route("/")
def home():

    return jsonify({

        "status": "running",

        "matches":
            len(cached_matches)

    })


@app.route("/matches")
def matches():

    return jsonify(
        cached_matches
    )


@app.route("/console")
def console():

    return jsonify(
        console_logs
    )


@app.route("/heatmap")
def heatmap():

    return jsonify(
        heatmap_cache
    )


@app.route("/live-events")
def live_events():

    return jsonify(
        live_events_cache[:40]
    )


def background_loop():

    while True:

        try:

            fetch_matches()

        except Exception as e:

            print(
                "BACKGROUND LOOP ERROR",
                e
            )

        time.sleep(6)


if __name__ == "__main__":

    try:

        fetch_matches()

        Thread(
            target=background_loop,
            daemon=True
        ).start()

        app.run(
            host="0.0.0.0",
            port=10000
        )

    except Exception as e:

        print(
            "SERVER START ERROR",
            e
        )

