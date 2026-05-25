
from flask import Flask, jsonify
from flask_cors import CORS

import random
import time

app = Flask(__name__)

CORS(app)

BOOKMAKERS = [
    "PIN",
    "365",
    "SBO",
    "IBC",
    "CMD",
    "188",
    "SABA",
    "BTI"
]

MATCHES = [

    ("PSG vs Arsenal", "UEFA Champions League", "UCL"),
    ("Manchester City vs Aston Villa", "England Premier League", "EPL"),
    ("Liverpool vs Brentford", "England Premier League", "EPL"),
    ("Brighton vs Manchester United", "England Premier League", "EPL"),
    ("Tottenham vs Everton", "England Premier League", "EPL"),
    ("Napoli vs Udinese", "Italy Serie A", "SA"),
    ("AC Milan vs Cagliari", "Italy Serie A", "SA"),
    ("Torino vs Juventus", "Italy Serie A", "SA"),
    ("Villarreal vs Atletico Madrid", "Spain La Liga", "LAL"),
    ("Saint-Étienne vs Nice", "France Ligue 1", "L1"),
    ("Paderborn vs Wolfsburg", "Germany Bundesliga", "BUN"),
    ("Inter Miami vs Philadelphia", "MLS", "MLS"),
    ("LAFC vs Seattle Sounders", "MLS", "MLS"),
    ("Ajax vs Utrecht", "Netherlands Eredivisie", "ERD"),
    ("Club Brugge vs Anderlecht", "Belgium First Division", "BEL"),
    ("Benfica vs Porto", "Portugal Liga", "POR")

]

def build_match(match_name, league_name, league_code):

    live = random.choice([True, True, True, False])

    home_score = random.randint(0, 3) if live else None
    away_score = random.randint(0, 3) if live else None

    arb = round(
        random.uniform(0.4, 4.8),
        2
    )

    heat_level = random.choice([
        "NORMAL",
        "HOT",
        "SHARP",
        "STEAM"
    ])

    book_a = random.choice(BOOKMAKERS)
    book_b = random.choice(BOOKMAKERS)

    while book_a == book_b:

        book_b = random.choice(
            BOOKMAKERS
        )

    return {

        "match":
            match_name,

        "league":
            league_code,

        "leagueName":
            league_name,

        "liveStatus":
            "LIVE" if live else "PRE",

        "clock":

            f"{random.randint(1,90)}'"

            if live

            else

            f"24/05 • {random.randint(16,23)}:{random.choice(['00','15','30','45'])}",

        "displayTime":

            f"{random.randint(1,90)}'"

            if live

            else

            "PRE",

        "homeScore":
            home_score,

        "awayScore":
            away_score,

        "bookA":
            book_a,

        "bookB":
            book_b,

        "awayOddA":
            round(
                random.uniform(0.84, 1.02),
                2
            ),

        "awayOddB":
            round(
                random.uniform(0.84, 1.02),
                2
            ),

        "movementDelta":
            round(
                random.uniform(0.01, 0.12),
                2
            ),

        "heatLevel":
            heat_level,

        "arbPercent":
            arb,

        "movementHistory": [

            round(random.uniform(0.86, 0.98), 2),

            round(random.uniform(0.86, 0.98), 2),

            round(random.uniform(0.86, 0.98), 2),

            round(random.uniform(0.86, 0.98), 2),

            round(random.uniform(0.86, 0.98), 2)

        ],

        "marketDepth": [

            random.choice(BOOKMAKERS),

            random.choice(BOOKMAKERS),

            random.choice(BOOKMAKERS),

            random.choice(BOOKMAKERS)

        ],

        "predictHome":
            random.randint(0, 3),

        "predictAway":
            random.randint(0, 3),

        "aiConfidence":
            random.randint(61, 94),

        "xGHome":
            round(
                random.uniform(0.4, 2.8),
                2
            ),

        "xGAway":
            round(
                random.uniform(0.4, 2.8),
                2
            ),

        "momentum":
            random.choice([
                "HOME_PRESSURE",
                "AWAY_PRESSURE",
                "BALANCED",
                "HIGH_TEMPO"
            ]),

        "workflowTriggers": [

            random.choice([
                "LIVE_ARB",
                "HOT_MOVEMENT",
                "STEAM_MOVE",
                "SHARP_ACTION"
            ]),

            random.choice([
                "LIVE_ARB",
                "HOT_MOVEMENT",
                "STEAM_MOVE",
                "SHARP_ACTION"
            ])

        ],

        "heatScore":
            random.randint(45, 98),

        "liquidityScore":
            random.randint(30, 100),

        "marketVelocity":
            round(
                random.uniform(0.5, 5.8),
                2
            ),

        "sharpMoney":
            random.choice([
                True,
                False
            ]),

        "steamMove":
            random.choice([
                True,
                False
            ])

    }

@app.route("/")
def home():

    return jsonify({

        "status": "LIVE",

        "server":
            "Premium Asian Terminal API",

        "markets":
            len(MATCHES),

        "timestamp":
            int(time.time())

    })

@app.route("/matches")
def matches():

    data = []

    for match in MATCHES:

        data.append(

            build_match(
                match[0],
                match[1],
                match[2]
            )

        )

    return jsonify(data)

@app.route("/health")
def health():

    return jsonify({

        "status":
            "healthy",

        "api":
            "running"

    })

if __name__ == "__main__":

    print("")
    print("===================================")
    print(" PREMIUM ASIAN TERMINAL API ")
    print("===================================")
    print(" API PORT : 10000")
    print("===================================")
    print("")

    app.run(

        host="0.0.0.0",

        port=10000,

        debug=True

    )

