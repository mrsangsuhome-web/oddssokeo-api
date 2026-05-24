
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

console_logs = []

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
    "soccer_korea_kleague1",
    "soccer_china_superleague",
    "soccer_australia_aleague",

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
    "soccer_poland_ekstraklasa"

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
    "SOCCER_BELGIUM_FIRST_DIV": "BEL",
    "SOCCER_TURKEY_SUPER_LIG": "TUR",
    "SOCCER_SWEDEN_ALLSVENSKAN": "SWE",
    "SOCCER_NORWAY_ELITESERIEN": "NOR",
    "SOCCER_DENMARK_SUPERLIGA": "DEN",

    "SOCCER_BRAZIL_CAMPEONATO": "BRA",
    "SOCCER_ARGENTINA_PRIMERA_DIVISION": "ARG",
    "SOCCER_CHILE_CAMPEONATO": "CHI",
    "SOCCER_MEXICO_LIGAMX": "MEX",

    "SOCCER_JAPAN_J_LEAGUE": "JPN",
    "SOCCER_KOREA_KLEAGUE1": "KOR",
    "SOCCER_CHINA_SUPERLEAGUE": "CHN",
    "SOCCER_AUSTRALIA_ALEAGUE": "AUS",

    "SOCCER_UEFA_CHAMPS_LEAGUE": "UCL",
    "SOCCER_UEFA_EUROPA_LEAGUE": "UEL",
    "SOCCER_UEFA_EUROPA_CONFERENCE_LEAGUE": "UECL",

    "SOCCER_FIFA_WORLD_CUP": "WC",
    "SOCCER_FIFA_WORLD_CUP_WOMEN": "WWC",

    "SOCCER_ENGLAND_CHAMPIONSHIP": "EFL",
    "SOCCER_ENGLAND_LEAGUE1": "L1 ENG",
    "SOCCER_ENGLAND_LEAGUE2": "L2 ENG",

    "SOCCER_SCOTLAND_PREMIERSHIP": "SCO",
    "SOCCER_SWITZERLAND_SUPERLEAGUE": "SUI",
    "SOCCER_AUSTRIA_BUNDESLIGA": "AUT",
    "SOCCER_POLAND_EKSTRAKLASA": "POL"

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


def normalize_bookmaker(name):

    if not name:
        return None

    upper_name = name.upper()

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

    scores = game.get("scores", {})

    home_score = scores.get(
        "home",
        0
    )

    away_score = scores.get(
        "away",
        0
    )

    clock = game.get(
        "clock",
        None
    )

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

            "displayTime": None,

            "clock": "FT",

            "minute": 90,

            "injury": 0,

            "homeScore": home_score,

            "awayScore": away_score

        }

    if clock:

        minute = 0

        try:

            minute = int(
                clock.split(":")[0]
            )

        except:
            pass

        status = "H1"

        if minute >= 46:
            status = "H2"

        return {

            "liveStatus": status,

            "displayTime": None,

            "clock": clock,

            "minute": minute,

            "injury": 0,

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

        local_time = match_time.astimezone()

        return {

            "liveStatus": "PRE",

            "displayTime":
                local_time.strftime(
                    "%d/%m • %H:%M"
                ),

            "clock": None,

            "minute": 0,

            "injury": 0,

            "homeScore": None,

            "awayScore": None

        }

    except:

        return {

            "liveStatus": "PRE",

            "displayTime": "--/-- • --:--",

            "clock": None,

            "minute": 0,

            "injury": 0,

            "homeScore": None,

            "awayScore": None

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

                commence_time = game.get(
                    "commence_time",
                    ""
                )

                market = "FT O/U"

                line = "2.5"

                bookA = "PIN"
                bookB = "365"

                awayOddA = 0.91
                awayOddB = 0.93

                homeOddA = 0.89
                homeOddB = 0.87

                real_books = []

                for b in bookmakers:

                    title = b.get("title")

                    normalized = normalize_bookmaker(
                            title
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

                        first_book =
                            bookmakers[0]

                        markets =
                            first_book.get(
                                "markets",
                                []
                            )

                        if markets:

                            market_data =
                                markets[0]

                            market =
                                market_data.get(
                                    "key",
                                    "FT O/U"
                                )

                            outcomes =
                                market_data.get(
                                    "outcomes",
                                    []
                                )

                            if len(outcomes) >= 2:

                                awayOddA =
                                    safe_float(
                                        outcomes[0].get(
                                            "price",
                                            0.91
                                        )
                                    )

                                homeOddA =
                                    safe_float(
                                        outcomes[1].get(
                                            "price",
                                            0.89
                                        )
                                    )

                                line =
                                    str(
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

                liveData =
                    parse_live_data(
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
                            f"{bookA} updated {home_team} vs {away_team} gap +{gap}"

                    }

                )

                console_logs[:] =
                    console_logs[:30]

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

                    "clock":
                        liveData["clock"],

                    "minute":
                        liveData["minute"],

                    "injury":
                        liveData["injury"],

                    "homeScore":
                        liveData["homeScore"],

                    "awayScore":
                        liveData["awayScore"],

                    "timestamp":
                        int(time.time())

                })

        def sort_priority(item):

            live_order = {

                "H1": 0,
                "H2": 1,
                "HT": 2,
                "PRE": 3,
                "FIN": 4

            }

            return (

                live_order.get(
                    item["liveStatus"],
                    99
                ),

                -item["gap"],

                -item["timestamp"]

            )

        cached_matches = sorted(

            results,

            key=sort_priority

        )[:60]

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


@app.route("/console")
def console():

    return jsonify(
        console_logs
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

