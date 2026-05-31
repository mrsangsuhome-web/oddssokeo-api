from flask import Flask, jsonify
from flask_cors import CORS

import requests
import time
import json
import os

from threading import Thread
from dotenv import load_dotenv

load_dotenv()

app = Flask(**name**)

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

"soccer_uefa_champs_league",
"soccer_uefa_europa_league",
"soccer_uefa_europa_conference_league",

"soccer_fifa_world_cup",

"soccer_england_championship"


]

BOOKMAKERS = [


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

LEAGUE_MAP = {


"SOCCER_EPL": "EPL",
"SOCCER_USA_MLS": "MLS",
"SOCCER_SPAIN_LA_LIGA": "LAL",
"SOCCER_GERMANY_BUNDESLIGA": "BUN",
"SOCCER_ITALY_SERIE_A": "SA",
"SOCCER_FRANCE_LIGUE_ONE": "L1",

"SOCCER_UEFA_CHAMPS_LEAGUE": "UCL",
"SOCCER_UEFA_EUROPA_LEAGUE": "UEL",
"SOCCER_UEFA_EUROPA_CONFERENCE_LEAGUE": "UECL",

"SOCCER_FIFA_WORLD_CUP": "WC",

"SOCCER_ENGLAND_CHAMPIONSHIP": "EFL"


}
def fetch_odds():

global cached_matches

results = []

headers = {

    "X-API-Key": API_KEY

}

try:

    for sport in SPORTS:

        url = (
            f"https://parlay-api.com/v1/"
            f"sports/{sport}/events"
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

            home = game.get(
                "home_team",
                "HOME"
            )

            away = game.get(
                "away_team",
                "AWAY"
            )

            results.append({

                "match":
                    f"{home} vs {away}",

                "league":
                    LEAGUE_MAP.get(
                        sport.upper(),
                        sport.upper()
                    ),

                "bookA":
                    BOOKMAKERS[0],

                "bookB":
                    BOOKMAKERS[1],

                "awayOddA":
                    0.95,

                "awayOddB":
                    0.97,

                "gap":
                    0.02,

                "liveStatus":
                    "LIVE",

                "timestamp":
                    int(time.time())

            })

    cached_matches = results[:200]

    with open(
        CACHE_FILE,
        "w"
    ) as f:

        json.dump(
            cached_matches,
            f
        )

    console_logs.insert(

        0,

        {

            "time":
                time.strftime("%H:%M:%S"),

            "message":
                f"UPDATED {len(cached_matches)} MATCHES"

        }

    )

    console_logs[:] = console_logs[:50]

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

    time.sleep(15)

if **name** == "**main**":

fetch_odds()

Thread(

    target=background_loop,

    daemon=True

).start()

app.run(

    host="0.0.0.0",

    port=10000

)



