
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
    ("Benfica vs Porto", "Portugal Liga", "POR"),
    ("Flamengo vs Palmeiras", "Brazil Serie A", "BRA"),
    ("Boca Juniors vs River Plate", "Argentina Primera", "ARG"),
    ("Galatasaray vs Fenerbahce", "Turkey Super Lig", "TUR"),
    ("Celtic vs Rangers", "Scotland Premiership", "SCO")

]

def generate_movement():

    values = []

    for _ in range(8):

        values.append(

            round(
                random.uniform(0.84, 1.02),
                2
            )

        )

    return values

def generate_depth():

    depth = []

    for _ in range(6):

        liquidity = random.randint(15, 100)

        depth.append({

            "book":
                random.choice(
                    BOOKMAKERS
                ),

            "odd":
                round(
                    random.uniform(0.84, 1.02),
                    2
                ),

            "liquidity":
                liquidity,

            "side":
                random.choice([
                    "BACK",
                    "LAY"
                ]),

            "pressure":
                random.choice([
                    "LOW",
                    "MEDIUM",
                    "HIGH"
                ])

        })

    return depth

def ai_prediction():

    home = random.randint(0, 3)

    away = random.randint(0, 3)

    confidence = random.randint(61, 96)

    return {

        "predictHome":
            home,

        "predictAway":
            away,

        "confidence":
            confidence,

        "xGHome":
            round(
                random.uniform(0.5, 2.8),
                2
            ),

        "xGAway":
            round(
                random.uniform(0.5, 2.8),
                2
            ),

        "pressureIndex":
            random.randint(40, 99),

        "tempo":
            random.choice([
                "LOW",
                "NORMAL",
                "HIGH"
            ])

    }

def workflow_engine(arb, heat, velocity):

    triggers = []

    if arb >= 2:

        triggers.append(
            "LIVE_ARB"
        )

    if heat >= 80:

        triggers.append(
            "HOT_MOVEMENT"
        )

    if velocity >= 4:

        triggers.append(
            "STEAM_MOVE"
        )

    if arb >= 3:

        triggers.append(
            "VALUE_BET"
        )

    if arb >= 3 and velocity >= 4:

        triggers.append(
            "PRIORITY_ALERT"
        )

    if random.choice([True, False]):

        triggers.append(
            "SHARP_ACTION"
        )

    return triggers

def build_match(match_name, league_name, league_code):

    live = random.choice([
        True,
        True,
        True,
        False
    ])

    home_score = random.randint(0, 4) if live else None
    away_score = random.randint(0, 4) if live else None

    arb = round(
        random.uniform(0.5, 5.5),
        2
    )

    heat_score = random.randint(40, 99)

    velocity = round(
        random.uniform(0.4, 6.8),
        2
    )

    heat_level = random.choice([
        "NORMAL",
        "HOT",
        "SHARP",
        "STEAM"
    ])

    book_a = random.choice(
        BOOKMAKERS
    )

    book_b = random.choice(
        BOOKMAKERS
    )

    while book_a == book_b:

        book_b = random.choice(
            BOOKMAKERS
        )

    ai = ai_prediction()

    sharp_money = random.choice([
        True,
        False
    ])

    steam_move = random.choice([
        True,
        False
    ])

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
                random.uniform(0.01, 0.14),
                2
            ),

        "heatLevel":
            heat_level,

        "heatScore":
            heat_score,

        "arbPercent":
            arb,

        "movementHistory":
            generate_movement(),

        "marketDepth":
            generate_depth(),

        "predictHome":
            ai["predictHome"],

        "predictAway":
            ai["predictAway"],

        "aiConfidence":
            ai["confidence"],

        "xGHome":
            ai["xGHome"],

        "xGAway":
            ai["xGAway"],

        "pressureIndex":
            ai["pressureIndex"],

        "tempo":
            ai["tempo"],

        "momentum":
            random.choice([
                "HOME_PRESSURE",
                "AWAY_PRESSURE",
                "BALANCED",
                "HIGH_TEMPO"
            ]),

        "workflowTriggers":
            workflow_engine(
                arb,
                heat_score,
                velocity
            ),

        "liquidityScore":
            random.randint(30, 100),

        "marketVelocity":
            velocity,

        "sharpMoney":
            sharp_money,

        "steamMove":
            steam_move,

        "signalStrength":
            random.randint(40, 100),

        "marketPressure":
            random.choice([
                "BUY_PRESSURE",
                "SELL_PRESSURE",
                "BALANCED"
            ]),

        "created":
            int(time.time())

    }

@app.route("/")
def home():

    return jsonify({

        "status":
            "LIVE",

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

@app.route("/analytics")
def analytics():

    markets = []

    for match in MATCHES:

        markets.append(

            build_match(
                match[0],
                match[1],
                match[2]
            )

        )

    return jsonify({

        "markets":
            markets,

        "hotCount":

            len([
                x for x in markets
                if x["heatLevel"] != "NORMAL"
            ]),

        "arbCount":

            len([
                x for x in markets
                if x["arbPercent"] >= 2
            ]),

        "sharpCount":

            len([
                x for x in markets
                if x["sharpMoney"]
            ]),

        "steamCount":

            len([
                x for x in markets
                if x["steamMove"]
            ])

    })

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

