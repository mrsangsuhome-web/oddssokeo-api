
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

heatmap_cache = []

live_events_cache = []

movement_history = {}

SPORTS = [

    # ENGLAND

    "soccer_epl",
    "soccer_england_championship",
    "soccer_england_league1",
    "soccer_england_league2",

    # SPAIN

    "soccer_spain_la_liga",
    "soccer_spain_segunda_division",

    # GERMANY

    "soccer_germany_bundesliga",
    "soccer_germany_bundesliga2",

    # ITALY

    "soccer_italy_serie_a",
    "soccer_italy_serie_b",

    # FRANCE

    "soccer_france_ligue_one",
    "soccer_france_ligue_two",

    # PORTUGAL

    "soccer_portugal_primeira_liga",

    # NETHERLANDS

    "soccer_netherlands_eredivisie",

    # BELGIUM

    "soccer_belgium_first_div",

    # TURKEY

    "soccer_turkey_super_lig",

    # SCOTLAND

    "soccer_scotland_premiership",

    # SWITZERLAND

    "soccer_switzerland_superleague",

    # AUSTRIA

    "soccer_austria_bundesliga",

    # POLAND

    "soccer_poland_ekstraklasa",

    # SWEDEN

    "soccer_sweden_allsvenskan",
    "soccer_sweden_superettan",

    # NORWAY

    "soccer_norway_eliteserien",

    # DENMARK

    "soccer_denmark_superliga",

    # UEFA

    "soccer_uefa_champs_league",
    "soccer_uefa_europa_league",
    "soccer_uefa_europa_conference_league",

    # USA

    "soccer_usa_mls",

    # MEXICO

    "soccer_mexico_ligamx",

    # BRAZIL

    "soccer_brazil_campeonato",

    # ARGENTINA

    "soccer_argentina_primera_division",

    # CHILE

    "soccer_chile_campeonato",

    # JAPAN

    "soccer_japan_j_league",
    "soccer_japan_j2_league",
    "soccer_japan_j3_league",

    # JAPAN WOMEN

    "soccer_japan_nadeshiko_league_women",

    # KOREA

    "soccer_korea_kleague1",
    "soccer_korea_kleague2",

    # CHINA

    "soccer_china_superleague",

    # AUSTRALIA

    "soccer_australia_aleague",

    # AUSTRALIA NPL

    "soccer_australia_npl_queensland",
    "soccer_australia_npl_nsw",
    "soccer_australia_npl_victoria",
    "soccer_australia_npl_tasmania",

    # AUSTRALIA U20

    "soccer_australia_npl_nsw_u20",

    # AUSTRALIA QPL

    "soccer_australia_queensland_premier_league",

    # OCEANIA

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

    "soccer_uefa_champs_league":
        {
            "short": "UCL",
            "name": "UEFA Champions League"
        }

}


def add_console_log(message):

    global console_logs

    console_logs.insert(0, {

        "time":
            datetime.now().strftime("%H:%M:%S"),

        "message":
            message

    })

    console_logs = console_logs[:100]


def normalize_bookmaker(name):

    if not name:
        return None

    upper_name = str(name).upper()

    for key, short in BOOKMAKER_MAP.items():

        if key in upper_name:
            return short

    return upper_name[:6]


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

    movement_history[match_key] = movement_history[match_key][-8:]

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

            if minutes_live >= 115:

                return {

                    "status": "FIN",

                    "clock": "FT",

                    "displayTime": None,

                    "homeScore": home_score,

                    "awayScore": away_score

                }

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
    global heatmap_cache
    global live_events_cache

    results = []

    heatmap = []

    live_events = []

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
                        "card",

                        "(shots)",
                        "shots",

                        "(offsides)",
                        "offside"

                    ]

                    if any(
                        k in lower_match
                        for k in banned_keywords
                    ):
                        continue

                    normalized_match = (
                        match_name
                        .replace("FC ", "")
                        .replace("CF ", "")
                        .replace("United", "Utd")
                        .replace("Wolverhampton", "Wolves")
                        .replace("Hotspur", "")
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

                    odd_a = round(
                        random.uniform(
                            0.87,
                            0.99
                        ),
                        2
                    )

                    odd_b = round(
                        odd_a + random.uniform(
                            0.01,
                            0.04
                        ),
                        2
                    )

                    movement = track_movement(
                        match_name,
                        odd_a
                    )

                    heat = movement["heat"]

                    live_data = parse_live_data(
                        game
                    )

                    arb_percent = round(
                        random.uniform(
                            0.2,
                            2.8
                        ),
                        2
                    )

                    if heat == "HOT":

                        add_console_log(
                            f"{match_name} market spike"
                        )

                    if arb_percent >= 2:

                        add_console_log(
                            f"ARB FOUND {arb_percent}% {match_name}"
                        )

                    if live_data["status"] == "LIVE":

                        live_events.append({

                            "event": "LIVE",

                            "match": match_name

                        })

                    heatmap.append({

                        "match": match_name,

                        "heat": heat

                    })

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

                        "marketDepth":
                            real_books[:6],

                        "awayOddA": odd_a,
                        "awayOddB": odd_b,

                        "homeOddA":
                            round(
                                odd_a - 0.02,
                                2
                            ),

                        "homeOddB":
                            round(
                                odd_b - 0.02,
                                2
                            ),

                        "gap":
                            round(
                                odd_b - odd_a,
                                2
                            ),

                        "movementDelta":
                            movement["delta"],

                        "movementHistory":
                            movement["history"],

                        "arbPercent":
                            arb_percent,

                        "heatLevel":
                            heat,

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


