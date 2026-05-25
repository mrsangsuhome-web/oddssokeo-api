
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
    "soccer_spain_la_liga",
    "soccer_germany_bundesliga",
    "soccer_italy_serie_a",
    "soccer_france_ligue_one",

    "soccer_usa_mls",
    "soccer_brazil_campeonato",
    "soccer_argentina_primera_division",

    "soccer_japan_j_league",
    "soccer_korea_kleague1",
    "soccer_china_superleague",

    "soccer_australia_aleague",

    "soccer_uefa_champs_league",
    "soccer_uefa_europa_league",

    "soccer_england_championship",

    "soccer_netherlands_eredivisie",
    "soccer_belgium_first_div"

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

    "soccer_uefa_champs_league":
        {
            "short": "UCL",
            "name": "UEFA Champions League"
        }

}

BOOKS = [

    "PIN",
    "365",
    "188",
    "SBO",
    "IBC",
    "CMD",
    "SABA",
    "BTI"

]


def add_console_log(message):

    global console_logs

    console_logs.insert(0, {

        "time":
            datetime.now().strftime("%H:%M:%S"),

        "message":
            message

    })

    console_logs = console_logs[:100]


def get_heat(delta):

    delta = abs(delta)

    if delta >= 0.05:
        return "HOT"

    if delta >= 0.03:
        return "WARM"

    return "NORMAL"


def track_movement(match_key, odd):

    global movement_history

    if match_key not in movement_history:

        movement_history[match_key] = [odd]

    movement_history[match_key].append(odd)

    movement_history[match_key] = movement_history[match_key][-10:]

    history = movement_history[match_key]

    if len(history) >= 2:

        delta = round(
            history[-1] - history[-2],
            2
        )

    else:

        delta = 0

    return {

        "history": history,

        "delta": delta,

        "heat": get_heat(delta)

    }


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

            if minutes_live >= 120:

                return {

                    "status": "FIN",

                    "clock": "FT",

                    "displayTime": None,

                    "homeScore": home_score,

                    "awayScore": away_score

                }

            if minutes_live <= 45:

                live_clock = f"{minutes_live}'"

            elif minutes_live <= 60:

                live_clock = "HT"

            elif minutes_live <= 105:

                live_clock = f"{minutes_live - 15}'"

            else:

                live_clock = "90+'"

            return {

                "status": "LIVE",

                "clock": live_clock,

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

            "displayTime": "--/--",

            "homeScore": None,

            "awayScore": None

        }


def fetch_matches():

    global cached_matches
    global heatmap_cache
    global live_events_cache

    results = []

    heatmap = []

    live_events = []

    seen = set()

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

                    home = game.get(
                        "home_team",
                        "HOME"
                    )

                    away = game.get(
                        "away_team",
                        "AWAY"
                    )

                    match = f"{home} vs {away}"

                    lower_match = match.lower()

                    banned = [

                        "(bookings)",
                        "(corners)",
                        "(cards)",
                        "booking",
                        "corner",
                        "card"

                    ]

                    if any(
                        b in lower_match
                        for b in banned
                    ):
                        continue

                    normalized = (
                        match
                        .replace("FC ", "")
                        .replace("United", "Utd")
                        .replace("Hotspur", "")
                        .replace("Wolverhampton", "Wolves")
                        .strip()
                        .lower()
                    )

                    if normalized in seen:
                        continue

                    seen.add(normalized)

                    live_data = parse_live_data(
                        game
                    )

                    bookA, bookB = random.sample(
                        BOOKS,
                        2
                    )

                    odd_a = round(
                        random.uniform(
                            0.87,
                            0.98
                        ),
                        2
                    )

                    odd_b = round(
                        odd_a + random.uniform(
                            0.01,
                            0.05
                        ),
                        2
                    )

                    movement = track_movement(
                        match,
                        odd_a
                    )

                    heat = movement["heat"]

                    arb_percent = round(

                        random.uniform(
                            0.3,
                            3.0
                        ),

                        2

                    )

                    if heat == "HOT":

                        add_console_log(
                            f"{match} market spike"
                        )

                    if arb_percent >= 2:

                        add_console_log(
                            f"ARB FOUND {arb_percent}% {match}"
                        )

                    if live_data["status"] == "LIVE":

                        live_events.append({

                            "event": "LIVE",

                            "match": match

                        })

                    heatmap.append({

                        "match": match,

                        "heat": heat

                    })

                    results.append({

                        "match": match,

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

                        "bookA": bookA,
                        "bookB": bookB,

                        "awayOddA": odd_a,
                        "awayOddB": odd_b,

                        "gap":
                            round(
                                odd_b - odd_a,
                                2
                            ),

                        "marketDepth":
                            random.sample(
                                BOOKS,
                                random.randint(
                                    3,
                                    6
                                )
                            ),

                        "movementHistory":
                            movement["history"],

                        "movementDelta":
                            movement["delta"],

                        "heatLevel":
                            heat,

                        "arbPercent":
                            arb_percent,

                        "liveStatus":
                            live_data["status"],

                        "clock":
                            live_data["clock"],

                        "displayTime":
                            live_data["displayTime"],

                        "homeScore":
                            live_data["homeScore"],

                        "awayScore":
                            live_data["awayScore"]

                    })

            except Exception as e:

                add_console_log(
                    f"SPORT ERROR {sport}"
                )

        results = sorted(

            results,

            key=lambda x: (

                x["liveStatus"] != "LIVE",

                -x["arbPercent"]

            )

        )

        cached_matches = results[:300]

        heatmap_cache = heatmap[:50]

        live_events_cache = live_events[:50]

        with open(
            CACHE_FILE,
            "w"
        ) as f:

            json.dump(
                cached_matches,
                f
            )

        add_console_log(
            f"UPDATED {len(cached_matches)} MARKETS"
        )

    except Exception as e:

        add_console_log(
            f"FETCH ERROR {e}"
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
        live_events_cache
    )


def background_loop():

    while True:

        try:

            fetch_matches()

        except Exception as e:

            add_console_log(
                f"BACKGROUND ERROR {e}"
            )

        time.sleep(6)


if __name__ == "__main__":

    fetch_matches()

    Thread(
        target=background_loop,
        daemon=True
    ).start()

    app.run(
        host="0.0.0.0",
        port=10000
    )

