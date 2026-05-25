
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
    "soccer_england_league1",
    "soccer_england_league2",

    "soccer_spain_la_liga",
    "soccer_spain_segunda_division",

    "soccer_germany_bundesliga",
    "soccer_germany_bundesliga2",

    "soccer_italy_serie_a",
    "soccer_italy_serie_b",

    "soccer_france_ligue_one",
    "soccer_france_ligue_two",

    "soccer_portugal_primeira_liga",

    "soccer_netherlands_eredivisie",

    "soccer_belgium_first_div",

    "soccer_turkey_super_lig",

    "soccer_scotland_premiership",

    "soccer_switzerland_superleague",

    "soccer_austria_bundesliga",

    "soccer_poland_ekstraklasa",

    "soccer_sweden_allsvenskan",
    "soccer_sweden_superettan",

    "soccer_norway_eliteserien",
    "soccer_denmark_superliga",

    "soccer_uefa_champs_league",
    "soccer_uefa_europa_league",
    "soccer_uefa_europa_conference_league",

    "soccer_usa_mls",

    "soccer_mexico_ligamx",

    "soccer_brazil_campeonato",

    "soccer_argentina_primera_division",

    "soccer_chile_campeonato",

    "soccer_japan_j_league",
    "soccer_japan_j2_league",
    "soccer_japan_j3_league",

    "soccer_japan_nadeshiko_league_women",

    "soccer_korea_kleague1",
    "soccer_korea_kleague2",

    "soccer_china_superleague",

    "soccer_australia_aleague",

    "soccer_australia_npl_queensland",
    "soccer_australia_npl_nsw",
    "soccer_australia_npl_victoria",
    "soccer_australia_npl_tasmania",

    "soccer_australia_npl_nsw_u20",

    "soccer_australia_queensland_premier_league",

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
    "BETINASIA": "BTI",
    "ISN": "ISN",
    "MAXBET": "MAX"

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

    "soccer_england_championship":
        {
            "short": "EFL",
            "name": "England Championship"
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

    "soccer_uefa_champs_league":
        {
            "short": "UCL",
            "name": "UEFA Champions League"
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

    "soccer_japan_j2_league":
        {
            "short": "J2",
            "name": "Japan J2 League"
        },

    "soccer_japan_j3_league":
        {
            "short": "J3",
            "name": "Japan J3 League"
        },

    "soccer_korea_kleague1":
        {
            "short": "K1",
            "name": "Korea K League 1"
        },

    "soccer_china_superleague":
        {
            "short": "CSL",
            "name": "China Super League"
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

    "soccer_australia_npl_queensland":
        {
            "short": "NPL QLD",
            "name": "Australia NPL Queensland"
        },

    "soccer_australia_npl_victoria":
        {
            "short": "NPL VIC",
            "name": "Australia NPL Victoria"
        },

    "soccer_australia_npl_tasmania":
        {
            "short": "NPL TAS",
            "name": "Australia NPL Tasmania"
        },

    "soccer_ofc_pro_league":
        {
            "short": "OFC",
            "name": "OFC Pro League"
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


def safe_float(value, default=0.91):

    try:
        return round(float(value), 2)
    except:
        return default


def get_heat(delta):

    abs_delta = abs(delta)

    if abs_delta >= 0.05:
        return "HOT"

    if abs_delta >= 0.03:
        return "WARM"

    return "NORMAL"


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

            for s in scores:

                score_name = str(
                    s.get("name", "")
                ).lower()

                score_value = int(
                    s.get("score", 0)
                )

                home_name = str(
                    game.get(
                        "home_team",
                        ""
                    )
                ).lower()

                away_name = str(
                    game.get(
                        "away_team",
                        ""
                    )
                ).lower()

                if home_name in score_name:
                    home_score = score_value

                if away_name in score_name:
                    away_score = score_value

        elif isinstance(scores, dict):

            home_score = int(
                scores.get(
                    "home",
                    0
                )
            )

            away_score = int(
                scores.get(
                    "away",
                    0
                )
            )

    except Exception as e:

        print("SCORE PARSE ERROR", e)

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

