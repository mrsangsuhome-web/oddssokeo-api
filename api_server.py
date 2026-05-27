
from flask import Flask, jsonify
from flask_cors import CORS

import sqlite3
import random
import time
import copy

app = Flask(__name__)

CORS(app)

DB_NAME = "market_history.db"

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

    ("PSG vs Arsenal", "UCL"),
    ("Manchester City vs Aston Villa", "EPL"),
    ("Liverpool vs Brentford", "EPL"),
    ("Tottenham vs Everton", "EPL"),
    ("Napoli vs Udinese", "SA"),
    ("AC Milan vs Cagliari", "SA"),
    ("Torino vs Juventus", "SA"),
    ("Villarreal vs Atletico Madrid", "LAL"),
    ("Saint-Étienne vs Nice", "L1"),
    ("Paderborn vs Wolfsburg", "BUN")

]

MARKET_MEMORY = {}

# =========================
# DATABASE
# =========================

def init_db():

    conn = sqlite3.connect(DB_NAME)

    cur = conn.cursor()

    cur.execute("""

        CREATE TABLE IF NOT EXISTS market_history (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            match_name TEXT,

            league TEXT,

            odd_a REAL,

            odd_b REAL,

            velocity REAL,

            arb REAL,

            cluster_name TEXT,

            confidence INTEGER,

            trend TEXT,

            reversal INTEGER,

            created INTEGER

        )

    """)

    conn.commit()

    conn.close()

# =========================
# SAVE HISTORY
# =========================

def save_history(market):

    conn = sqlite3.connect(DB_NAME)

    cur = conn.cursor()

    cur.execute("""

        INSERT INTO market_history (

            match_name,
            league,
            odd_a,
            odd_b,
            velocity,
            arb,
            cluster_name,
            confidence,
            trend,
            reversal,
            created

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

    """, (

        market["match"],
        market["league"],

        market["awayOddA"],
        market["awayOddB"],

        market["marketVelocity"],
        market["arbPercent"],

        market["cluster"],

        market["aiConfidence"],

        market["lastDirection"],

        int(market["trendReversal"]),

        int(time.time())

    ))

    conn.commit()

    conn.close()

# =========================
# INITIAL MARKET
# =========================

def create_initial_market(
    match_name,
    league
):

    odd_a = round(
        random.uniform(0.84, 1.02),
        2
    )

    odd_b = round(
        random.uniform(0.84, 1.02),
        2
    )

    return {

        "match":
            match_name,

        "league":
            league,

        "bookA":
            random.choice(
                BOOKMAKERS
            ),

        "bookB":
            random.choice(
                BOOKMAKERS
            ),

        "awayOddA":
            odd_a,

        "awayOddB":
            odd_b,

        "movementHistory": [
            odd_a for _ in range(40)
        ],

        "replayTimeline": [],

        "marketVelocity":
            0,

        "arbPercent":
            0,

        "cluster":
            "NORMAL",

        "steamMove":
            False,

        "sharpMoney":
            False,

        "syncLevel":
            0,

        "heatScore":
            40,

        "signalStrength":
            40,

        "aiConfidence":
            50,

        "lastDirection":
            "BALANCED",

        "trendReversal":
            False

    }

# =========================
# MOVEMENT ENGINE
# =========================

def weighted_move(history):

    recent = history[-6:]

    avg = sum(recent) / len(recent)

    latest = recent[-1]

    if latest > avg:

        choices = [
            0.01,
            0.02,
            0,
            -0.01
        ]

    else:

        choices = [
            -0.01,
            -0.02,
            0,
            0.01
        ]

    return random.choice(choices)

# =========================
# BUILD MARKET
# =========================

def build_market():

    global MARKET_MEMORY

    output = []

    for match in MATCHES:

        match_name = match[0]
        league = match[1]

        if match_name not in MARKET_MEMORY:

            MARKET_MEMORY[match_name] = create_initial_market(

                match_name,
                league

            )

        market = MARKET_MEMORY[match_name]

        prev_a = market["awayOddA"]
        prev_b = market["awayOddB"]

        move_a = weighted_move(
            market["movementHistory"]
        )

        move_b = weighted_move(
            market["movementHistory"]
        )

        next_a = round(
            prev_a + move_a,
            2
        )

        next_b = round(
            prev_b + move_b,
            2
        )

        next_a = max(
            0.75,
            min(1.15, next_a)
        )

        next_b = max(
            0.75,
            min(1.15, next_b)
        )

        velocity = round(

            abs(move_a) * 100 +

            abs(move_b) * 100,

            2

        )

        arb = round(
            abs(next_a - next_b) * 100,
            2
        )

        sync = 0

        if move_a > 0 and move_b > 0:
            sync = 1

        if move_a < 0 and move_b < 0:
            sync = 1

        steam = (
            velocity >= 5 and
            sync == 1
        )

        sharp = (
            arb >= 4
        )

        cluster = "NORMAL"

        if steam:
            cluster = "STEAM_CLUSTER"

        elif sharp:
            cluster = "SHARP_CLUSTER"

        elif velocity >= 3:
            cluster = "HOT_CLUSTER"

        trend = "BALANCED"

        if move_a > 0:
            trend = "UP"

        if move_a < 0:
            trend = "DOWN"

        reversal = False

        if market["lastDirection"] != trend:

            if market["lastDirection"] != "BALANCED":

                reversal = True

        confidence = min(

            99,

            int(
                velocity * 8 +
                arb * 8 +
                sync * 15
            )

        )

        replay = market["replayTimeline"]

        replay.append({

            "time":
                int(time.time()),

            "odd":
                next_a,

            "velocity":
                velocity,

            "arb":
                arb,

            "trend":
                trend

        })

        if len(replay) > 50:

            replay.pop(0)

        movement = market["movementHistory"]

        movement.append(next_a)

        if len(movement) > 40:

            movement.pop(0)

        market["awayOddA"] = next_a
        market["awayOddB"] = next_b

        market["marketVelocity"] = velocity

        market["arbPercent"] = arb

        market["syncLevel"] = sync

        market["steamMove"] = steam

        market["sharpMoney"] = sharp

        market["cluster"] = cluster

        market["movementHistory"] = movement

        market["replayTimeline"] = replay

        market["lastDirection"] = trend

        market["trendReversal"] = reversal

        market["aiConfidence"] = confidence

        market["signalStrength"] = confidence

        market["heatScore"] = min(
            99,
            int(
                velocity * 10 +
                arb * 8
            )
        )

        market["clock"] = f"{random.randint(1,90)}'"

        market["liveStatus"] = "LIVE"

        market["homeScore"] = random.randint(0, 3)

        market["awayScore"] = random.randint(0, 3)

        save_history(market)

        output.append(
            copy.deepcopy(market)
        )

    return output

# =========================
# ROUTES
# =========================

@app.route("/")
def home():

    return jsonify({

        "status":
            "LIVE",

        "engine":
            "SPORTSBOOK INTELLIGENCE ENGINE",

        "database":
            "SQLITE ACTIVE",

        "markets":
            len(MATCHES),

        "timestamp":
            int(time.time())

    })

@app.route("/matches")
def matches():

    return jsonify(
        build_market()
    )

@app.route("/history")
def history():

    conn = sqlite3.connect(DB_NAME)

    cur = conn.cursor()

    cur.execute("""

        SELECT

            match_name,
            league,
            odd_a,
            odd_b,
            velocity,
            arb,
            cluster_name,
            confidence,
            trend,
            reversal,
            created

        FROM market_history

        ORDER BY id DESC

        LIMIT 300

    """)

    rows = cur.fetchall()

    conn.close()

    output = []

    for row in rows:

        output.append({

            "match":
                row[0],

            "league":
                row[1],

            "oddA":
                row[2],

            "oddB":
                row[3],

            "velocity":
                row[4],

            "arb":
                row[5],

            "cluster":
                row[6],

            "confidence":
                row[7],

            "trend":
                row[8],

            "reversal":
                bool(row[9]),

            "created":
                row[10]

        })

    return jsonify(output)

@app.route("/health")
def health():

    return jsonify({

        "status":
            "healthy",

        "database":
            "connected",

        "engine":
            "replay intelligence active"

    })

# =========================
# START
# =========================

if __name__ == "__main__":

    init_db()

    print("")
    print("===================================")
    print(" SPORTSBOOK INTELLIGENCE ENGINE ")
    print("===================================")
    print(" API PORT : 10000")
    print(" DATABASE : SQLITE")
    print("===================================")
    print("")

    app.run(

        host="0.0.0.0",

        port=10000,

        debug=True

    )

