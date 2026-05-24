
from flask import Flask, jsonify
from flask_cors import CORS

import requests
import random
import time
import json
import os

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

source_health_cache = []

arb_cache = []

SPORTS = [

    "soccer_epl",
    "soccer_usa_mls",
    "soccer_spain_la_liga",
    "soccer_germany_bundesliga",
    "soccer_italy_serie_a",
    "soccer_france_ligue_one",

    "soccer_portugal_primeira_liga",
    "soccer_netherlands_eredivisie",
    "soccer_belgium_first_div",
    "soccer_turkey_super_lig",

    "soccer_sweden_allsvenskan",
    "soccer_norway_eliteserien",
    "soccer_denmark_superliga",

    "soccer_brazil_campeonato",
    "soccer_argentina_primera_division",
    "soccer_chile_campeonato",
    "soccer_mexico_ligamx",

    "soccer_japan_j_league",
    "soccer_japan_j2_league",
    "soccer_japan_j3_league",

    "soccer_korea_kleague1",
    "soccer_korea_kleague2",

    "soccer_china_superleague",
    "soccer_china_league_one",

    "soccer_australia_aleague",

    "soccer_australia_npl_queensland",
    "soccer_australia_npl_nsw",
    "soccer_australia_npl_victoria",
    "soccer_australia_npl_tasmania",

    "soccer_australia_queensland_premier_league",

    "soccer_australia_npl_nsw_u20",

    "soccer_uefa_champs_league",
    "soccer_uefa_europa_league",
    "soccer_uefa_europa_conference_league",

    "soccer_fifa_world_cup",
    "soccer_fifa_world_cup_women",

    "soccer_england_championship",
    "soccer_england_league1",
    "soccer_england_league2",

    "soccer_scotland_premiership",
    "soccer_switzerland_superleague",
    "soccer_austria_bundesliga",
    "soccer_poland_ekstraklasa",

    "soccer_russia_fnl2",

    "soccer_japan_nadeshiko_league_women",

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

DEFAULT_BOOKMAKERS = [

    "PIN",
    "365",
    "188",
    "SBO",
    "IBC",
    "CMD",
    "SABA",
    "BTI",
    "ISN",
    "MAX"

]

LEAGUE_NAMES = {

    "soccer_epl":
        {
            "short": "EPL",
            "name": "England Premier League"
        },

    "soccer_usa_mls":
        {
            "short": "MLS",
            "name": "USA Major League Soccer"
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

    "soccer_uefa_champs_league":
        {
            "short": "UCL",
            "name": "UEFA Champions League"
        },

    "soccer_uefa_europa_league":
        {
            "short": "UEL",
            "name": "UEFA Europa League"
        },

    "soccer_uefa_europa_conference_league":
        {
            "short": "UECL",
            "name": "UEFA Europa Conference League"
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


def parse_live_data(game):

    scores = game.get(
        "scores",
        {}
    )

    home_score = scores.get(
        "home",
        0
    )

    away_score = scores.get(
        "away",
        0
    )

    clock = game.get("clock")

    completed = game.get(
        "completed",
        False
    )

    commence_time = game.get(
        "commence_time",
        ""
    )

    if completed:

        return {

            "liveStatus": "FIN",

            "clock": "FT",

            "displayTime": None,

            "homeScore": home_score,

            "awayScore": away_score

        }

    if clock:

        return {

            "liveStatus": "LIVE",

            "clock": clock,

            "displayTime": None,

            "homeScore": home_score,

            "awayScore": away_score

        }

    try:

        match_time = datetime.fromisoformat(
            commence_time.replace(
                "Z",
                "+00:00"
            )
        )

        return {

            "liveStatus": "PRE",

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

            "liveStatus": "PRE",

            "clock": None,

            "displayTime": "--/-- • --:--",

            "homeScore": None,

            "awayScore": None

        }


def fetch_live_matches():

    global cached_matches

    results = []

    try:

        headers = {
            "X-API-Key": API_KEY
        }

        for sport in SPORTS:

            try:

                live_url = (
                    f"https://parlay-api.com/v1/"
                    f"sports/{sport}/live"
                )

                response = requests.get(
                    live_url,
                    headers=headers,
                    timeout=12
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

                    line = "2.5"

                    market = "FT O/U"

                    awayOddA = 0.91
                    homeOddA = 0.89

                    awayOddB = 0.93
                    homeOddB = 0.87

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

                        bookA, bookB = random.sample(
                            real_books,
                            2
                        )

                    else:

                        bookA, bookB = random.sample(
                            DEFAULT_BOOKMAKERS,
                            2
                        )

                    if bookmakers:

                        try:

                            markets = bookmakers[0].get(
                                "markets",
                                []
                            )

                            if markets:

                                market_data = markets[0]

                                market = market_data.get(
                                    "key",
                                    "FT O/U"
                                )

                                outcomes = market_data.get(
                                    "outcomes",
                                    []
                                )

                                if len(outcomes) >= 2:

                                    awayOddA = safe_float(
                                        outcomes[0].get(
                                            "price",
                                            0.91
                                        )
                                    )

                                    homeOddA = safe_float(
                                        outcomes[1].get(
                                            "price",
                                            0.89
                                        )
                                    )

                                    line = str(
                                        outcomes[0].get(
                                            "point",
                                            "2.5"
                                        )
                                    )

                        except:
                            pass

                    awayOddB = round(
                        awayOddA +
                        random.choice([
                            -0.02,
                            -0.01,
                            0.01,
                            0.02
                        ]),
                        2
                    )

                    homeOddB = round(
                        homeOddA +
                        random.choice([
                            -0.02,
                            -0.01,
                            0.01,
                            0.02
                        ]),
                        2
                    )

                    gap = round(
                        abs(
                            awayOddA -
                            awayOddB
                        ),
                        2
                    )

                    movement_score = round(
                        gap *
                        random.uniform(1, 3),
                        2
                    )

                    live_data = parse_live_data(
                        game
                    )

                    console_logs.insert(

                        0,

                        {

                            "time":
                                datetime.now().strftime(
                                    "%H:%M:%S"
                                ),

                            "message":
                                f"LIVE {home_team} vs {away_team} movement +{movement_score}"

                        }

                    )

                    console_logs[:] = console_logs[:40]

                    results.append({

                        "match":
                            f"{home_team} vs {away_team}",

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

                        "market": market,

                        "line": line,

                        "bookA": bookA,
                        "bookB": bookB,

                        "awayOddA": awayOddA,
                        "awayOddB": awayOddB,

                        "homeOddA": homeOddA,
                        "homeOddB": homeOddB,

                        "gap": gap,

                        "movementScore":
                            movement_score,

                        "liveStatus":
                            live_data["liveStatus"],

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
                    f"SPORT ERROR {sport}",
                    e
                )

        results = sorted(

            results,

            key=lambda x: (

                x["liveStatus"] != "LIVE",

                -x.get(
                    "movementScore",
                    0
                ),

                -x["gap"]

            )

        )

        cached_matches = results[:120]

        with open(
            CACHE_FILE,
            "w"
        ) as f:

            json.dump(
                cached_matches,
                f
            )

        print(
            f"UPDATED {len(cached_matches)} LIVE MATCHES"
        )

    except Exception as e:

        print("FETCH ERROR", e)


def fetch_arbs():

    global arb_cache

    try:

        headers = {
            "X-API-Key": API_KEY
        }

        url = (
            "https://parlay-api.com/v1/"
            "inplay/arbs"
        )

        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:

            data = response.json()

            if isinstance(data, list):
                arb_cache = data[:20]

    except Exception as e:

        print("ARB ERROR", e)


def fetch_source_health():

    global source_health_cache

    try:

        headers = {
            "X-API-Key": API_KEY
        }

        results = []

        for sport in SPORTS[:10]:

            try:

                url = (
                    f"https://parlay-api.com/v1/"
                    f"sports/{sport}/live/source-health"
                )

                response = requests.get(
                    url,
                    headers=headers,
                    timeout=8
                )

                if response.status_code == 200:

                    data = response.json()

                    results.append({

                        "sport": sport,

                        "data": data

                    })

            except:
                pass

        source_health_cache = results

    except Exception as e:

        print("SOURCE HEALTH ERROR", e)


@app.route("/")
def home():

    return jsonify({

        "status": "running",

        "matches": len(cached_matches),

        "arbs": len(arb_cache)

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


@app.route("/arbs")
def arbs():

    return jsonify(
        arb_cache
    )


@app.route("/source-health")
def source_health():

    return jsonify(
        source_health_cache
    )


def background_loop():

    while True:

        fetch_live_matches()

        fetch_arbs()

        fetch_source_health()

        time.sleep(8)


if __name__ == "__main__":

    fetch_live_matches()

    fetch_arbs()

    fetch_source_health()

    Thread(
        target=background_loop,
        daemon=True
    ).start()

    app.run(
        host="0.0.0.0",
        port=10000
    )
