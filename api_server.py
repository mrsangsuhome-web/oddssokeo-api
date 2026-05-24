
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


def track_movement(match_id, odd):

    old = movement_history.get(
        match_id,
        odd
    )

    delta = round(
        odd - old,
        2
    )

    movement_history[match_id] = odd

    return {

        "old": old,

        "new": odd,

        "delta": delta,

        "heat": get_heat(delta)

    }


def fetch_matches():

    global cached_matches
    global heatmap_cache

    results = []

    heatmap = []

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

                    line = "2.5"

                    market = "FT O/U"

                    period_market = "FT"

                    awayOddA = 0.91
                    homeOddA = 0.89

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

                                if "1h" in market.lower():
                                    period_market = "1H"

                                elif "2h" in market.lower():
                                    period_market = "2H"

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

                    movement = track_movement(
                        match_name,
                        awayOddA
                    )

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

                    live_data = parse_live_data(
                        game
                    )

                    if movement["heat"] == "HOT":

                        live_events_cache.insert(

                            0,

                            {

                                "time":
                                    datetime.now().strftime(
                                        "%H:%M:%S"
                                    ),

                                "event":
                                    "⚡ ODDS SPIKE",

                                "match":
                                    match_name

                            }

                        )

                    heatmap.append({

                        "match":
                            match_name,

                        "heat":
                            movement["heat"],

                        "delta":
                            movement["delta"]

                    })

                    console_logs.insert(

                        0,

                        {

                            "time":
                                datetime.now().strftime(
                                    "%H:%M:%S"
                                ),

                            "message":
                                f"{match_name} movement {movement['delta']}"

                        }

                    )

                    console_logs[:] = console_logs[:50]

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

                        "market": market,

                        "periodMarket":
                            period_market,

                        "line": line,

                        "bookA": bookA,
                        "bookB": bookB,

                        "awayOddA": awayOddA,
                        "awayOddB": awayOddB,

                        "homeOddA": homeOddA,
                        "homeOddB": homeOddB,

                        "gap": gap,

                        "movementDelta":
                            movement["delta"],

                        "heatLevel":
                            movement["heat"],

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

                -abs(
                    x["movementDelta"]
                ),

                -x["gap"]

            )

        )

        cached_matches = results[:150]

        heatmap_cache = heatmap[:50]

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

        fetch_matches()

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

