
from flask import Flask, jsonify
from flask_cors import CORS

import random
import time
import copy

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
    ("Tottenham vs Everton", "England Premier League", "EPL"),
    ("Napoli vs Udinese", "Italy Serie A", "SA"),
    ("AC Milan vs Cagliari", "Italy Serie A", "SA"),
    ("Torino vs Juventus", "Italy Serie A", "SA"),
    ("Villarreal vs Atletico Madrid", "Spain La Liga", "LAL"),
    ("Saint-Étienne vs Nice", "France Ligue 1", "L1"),
    ("Paderborn vs Wolfsburg", "Germany Bundesliga", "BUN")

]

MARKET_MEMORY = {}

def initial_market(match_name, league_name, league_code):

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
            league_code,

        "leagueName":
            league_name,

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

            odd_a for _ in range(30)

        ],

        "velocityHistory": [

            0 for _ in range(20)

        ],

        "trendHistory": [],

        "marketVelocity":
            0,

        "arbPercent":
            round(
                abs(odd_a - odd_b) * 100,
                2
            ),

        "heatLevel":
            "NORMAL",

        "heatScore":
            45,

        "steamMove":
            False,

        "sharpMoney":
            False,

        "signalStrength":
            40,

        "syncLevel":
            0,

        "momentum":
            "BALANCED",

        "workflowTriggers": [],

        "replayTimeline": [],

        "lastDirection":
            "NONE",

        "created":
            int(time.time())

    }

def weighted_move(history):

    recent = history[-5:]

    avg = sum(recent) / len(recent)

    if avg > recent[0]:

        choices = [
            0.01,
            0.01,
            0.02,
            0,
            -0.01
        ]

    else:

        choices = [
            -0.01,
            -0.01,
            -0.02,
            0,
            0.01
        ]

    return random.choice(choices)

def calculate_velocity(delta_a, delta_b):

    return round(

        abs(delta_a) * 100 +

        abs(delta_b) * 100,

        2

    )

def detect_sync(delta_a, delta_b):

    if delta_a > 0 and delta_b > 0:
        return 1

    if delta_a < 0 and delta_b < 0:
        return 1

    return 0

def detect_heat(velocity, arb):

    if velocity >= 5:
        return "STEAM"

    if arb >= 4:
        return "SHARP"

    if velocity >= 3:
        return "HOT"

    return "NORMAL"

def build_market():

    global MARKET_MEMORY

    output = []

    for match in MATCHES:

        key = match[0]

        if key not in MARKET_MEMORY:

            MARKET_MEMORY[key] = initial_market(
                match[0],
                match[1],
                match[2]
            )

        market = MARKET_MEMORY[key]

        previous_a = market["awayOddA"]
        previous_b = market["awayOddB"]

        delta_a = weighted_move(
            market["movementHistory"]
        )

        delta_b = weighted_move(
            market["movementHistory"]
        )

        next_a = round(
            previous_a + delta_a,
            2
        )

        next_b = round(
            previous_b + delta_b,
            2
        )

        if next_a < 0.75:
            next_a = 0.75

        if next_a > 1.15:
            next_a = 1.15

        if next_b < 0.75:
            next_b = 0.75

        if next_b > 1.15:
            next_b = 1.15

        velocity = calculate_velocity(
            delta_a,
            delta_b
        )

        arb = round(
            abs(next_a - next_b) * 100,
            2
        )

        sync = detect_sync(
            delta_a,
            delta_b
        )

        heat = detect_heat(
            velocity,
            arb
        )

        steam = (
            velocity >= 5 and
            sync == 1
        )

        sharp = (
            arb >= 4
        )

        movement = market["movementHistory"]

        movement.append(next_a)

        if len(movement) > 30:

            movement.pop(0)

        velocity_history = market["velocityHistory"]

        velocity_history.append(
            velocity
        )

        if len(velocity_history) > 20:

            velocity_history.pop(0)

        trend = "BALANCED"

        if next_a > previous_a:
            trend = "UP"

        if next_a < previous_a:
            trend = "DOWN"

        trend_history = market["trendHistory"]

        trend_history.append(trend)

        if len(trend_history) > 15:

            trend_history.pop(0)

        replay = market["replayTimeline"]

        replay.append({

            "time":
                int(time.time()),

            "odd":
                next_a,

            "velocity":
                velocity,

            "arb":
                arb

        })

        if len(replay) > 25:

            replay.pop(0)

        triggers = []

        if arb >= 3:
            triggers.append("LIVE_ARB")

        if steam:
            triggers.append("STEAM_MOVE")

        if sharp:
            triggers.append("SHARP_ACTION")

        if velocity >= 5:
            triggers.append("VELOCITY_SPIKE")

        if arb >= 4 and steam:
            triggers.append("PRIORITY_ALERT")

        signal_strength = min(

            100,

            int(
                velocity * 10 +
                arb * 10 +
                sync * 20
            )

        )

        market["awayOddA"] = next_a
        market["awayOddB"] = next_b

        market["movementHistory"] = movement

        market["velocityHistory"] = velocity_history

        market["trendHistory"] = trend_history

        market["marketVelocity"] = velocity

        market["arbPercent"] = arb

        market["syncLevel"] = sync

        market["heatLevel"] = heat

        market["steamMove"] = steam

        market["sharpMoney"] = sharp

        market["workflowTriggers"] = triggers

        market["signalStrength"] = signal_strength

        market["momentum"] = trend

        market["replayTimeline"] = replay

        market["heatScore"] = min(
            99,
            int(
                velocity * 12 +
                arb * 8 +
                sync * 15
            )
        )

        market["lastDirection"] = trend

        market["clock"] = f"{random.randint(1,90)}'"

        market["liveStatus"] = "LIVE"

        market["homeScore"] = random.randint(0, 3)

        market["awayScore"] = random.randint(0, 3)

        output.append(
            copy.deepcopy(market)
        )

    return output

@app.route("/")
def home():

    return jsonify({

        "status":
            "LIVE",

        "engine":
            "TRUE MOVEMENT MEMORY ENGINE",

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

@app.route("/analytics")
def analytics():

    markets = build_market()

    return jsonify({

        "markets":
            markets,

        "steamCount":

            len([
                x for x in markets
                if x["steamMove"]
            ]),

        "sharpCount":

            len([
                x for x in markets
                if x["sharpMoney"]
            ]),

        "arbCount":

            len([
                x for x in markets
                if x["arbPercent"] >= 3
            ]),

        "velocityCount":

            len([
                x for x in markets
                if x["marketVelocity"] >= 5
            ])

    })

@app.route("/health")
def health():

    return jsonify({

        "status":
            "healthy",

        "engine":
            "movement replay active"

    })

if __name__ == "__main__":

    print("")
    print("===================================")
    print(" TRUE REPLAY ENGINE ")
    print("===================================")
    print(" API PORT : 10000")
    print("===================================")
    print("")

    app.run(

        host="0.0.0.0",

        port=10000,

        debug=True

    )

