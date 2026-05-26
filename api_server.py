
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
            odd_a for _ in range(40)
        ],

        "velocityHistory": [
            0 for _ in range(25)
        ],

        "trendHistory": [],

        "clusterHistory": [],

        "replayTimeline": [],

        "marketVelocity":
            0,

        "arbPercent":
            0,

        "steamMove":
            False,

        "sharpMoney":
            False,

        "syncLevel":
            0,

        "heatLevel":
            "NORMAL",

        "heatScore":
            40,

        "signalStrength":
            40,

        "momentum":
            "BALANCED",

        "workflowTriggers": [],

        "aiConfidence":
            50,

        "trendReversal":
            False,

        "cluster":
            "NORMAL",

        "lastDirection":
            "NONE"

    }

def weighted_move(history):

    recent = history[-6:]

    avg = sum(recent) / len(recent)

    latest = recent[-1]

    if latest > avg:

        pool = [
            0.01,
            0.02,
            0.01,
            0,
            -0.01
        ]

    else:

        pool = [
            -0.01,
            -0.02,
            -0.01,
            0,
            0.01
        ]

    return random.choice(pool)

def calc_velocity(a, b):

    return round(

        abs(a) * 100 +

        abs(b) * 100,

        2

    )

def detect_sync(a, b):

    if a > 0 and b > 0:
        return 1

    if a < 0 and b < 0:
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

def detect_cluster(velocity, steam, sharp):

    if steam and velocity >= 5:
        return "STEAM_CLUSTER"

    if sharp:
        return "SHARP_CLUSTER"

    if velocity >= 3:
        return "HOT_CLUSTER"

    return "NORMAL"

def ai_confidence(velocity, arb, sync, trend):

    score = 40

    score += velocity * 5
    score += arb * 4
    score += sync * 15

    if trend == "UP":
        score += 8

    if trend == "DOWN":
        score += 8

    return min(
        99,
        int(score)
    )

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

        prev_a = market["awayOddA"]
        prev_b = market["awayOddB"]

        delta_a = weighted_move(
            market["movementHistory"]
        )

        delta_b = weighted_move(
            market["movementHistory"]
        )

        next_a = round(
            prev_a + delta_a,
            2
        )

        next_b = round(
            prev_b + delta_b,
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

        velocity = calc_velocity(
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

        steam = (
            velocity >= 5 and
            sync == 1
        )

        sharp = (
            arb >= 4
        )

        heat = detect_heat(
            velocity,
            arb
        )

        cluster = detect_cluster(
            velocity,
            steam,
            sharp
        )

        movement = market["movementHistory"]

        movement.append(next_a)

        if len(movement) > 40:

            movement.pop(0)

        velocity_history = market["velocityHistory"]

        velocity_history.append(
            velocity
        )

        if len(velocity_history) > 25:

            velocity_history.pop(0)

        trend = "BALANCED"

        if next_a > prev_a:
            trend = "UP"

        if next_a < prev_a:
            trend = "DOWN"

        reversal = False

        trend_history = market["trendHistory"]

        if len(trend_history) > 0:

            last = trend_history[-1]

            if last != trend and last != "BALANCED":

                reversal = True

        trend_history.append(trend)

        if len(trend_history) > 20:

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
                arb,

            "trend":
                trend

        })

        if len(replay) > 35:

            replay.pop(0)

        cluster_history = market["clusterHistory"]

        cluster_history.append(cluster)

        if len(cluster_history) > 20:

            cluster_history.pop(0)

        triggers = []

        if arb >= 3:
            triggers.append("LIVE_ARB")

        if steam:
            triggers.append("STEAM_MOVE")

        if sharp:
            triggers.append("SHARP_ACTION")

        if velocity >= 5:
            triggers.append("VELOCITY_SPIKE")

        if reversal:
            triggers.append("TREND_REVERSAL")

        confidence = ai_confidence(
            velocity,
            arb,
            sync,
            trend
        )

        market["awayOddA"] = next_a
        market["awayOddB"] = next_b

        market["movementHistory"] = movement

        market["velocityHistory"] = velocity_history

        market["trendHistory"] = trend_history

        market["clusterHistory"] = cluster_history

        market["marketVelocity"] = velocity

        market["arbPercent"] = arb

        market["syncLevel"] = sync

        market["steamMove"] = steam

        market["sharpMoney"] = sharp

        market["heatLevel"] = heat

        market["cluster"] = cluster

        market["signalStrength"] = confidence

        market["heatScore"] = min(
            99,
            int(
                velocity * 10 +
                arb * 8 +
                sync * 12
            )
        )

        market["workflowTriggers"] = triggers

        market["momentum"] = trend

        market["replayTimeline"] = replay

        market["lastDirection"] = trend

        market["trendReversal"] = reversal

        market["aiConfidence"] = confidence

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
            "TRUE MARKET INTELLIGENCE ENGINE",

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

        "reversalCount":

            len([
                x for x in markets
                if x["trendReversal"]
            ]),

        "clusterCount":

            len([
                x for x in markets
                if x["cluster"] != "NORMAL"
            ])

    })

@app.route("/health")
def health():

    return jsonify({

        "status":
            "healthy",

        "engine":
            "market intelligence active"

    })

if __name__ == "__main__":

    print("")
    print("===================================")
    print(" TRUE MARKET INTELLIGENCE ENGINE ")
    print("===================================")
    print(" API PORT : 10000")
    print("===================================")
    print("")

    app.run(

        host="0.0.0.0",

        port=10000,

        debug=True

    )

