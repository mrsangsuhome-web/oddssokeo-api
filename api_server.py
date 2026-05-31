
from flask import Flask, jsonify
from flask_cors import CORS

import sqlite3
import random
import time
import copy

app = Flask(__name__)

CORS(app)

DB_NAME = "market_history.db"

import requests

PARLAY_API_KEY = "YOUR_API_KEY"

BASE_URL = "https://parlay-api.com/v1"

BOOKMAKERS = [

```
"PIN",
"365",
"SBO",
"IBC",
"188",

"SABA",
"CMD",
"BTI"
```

]

def get_active_soccer_sports():

```
headers = {

    "X-API-Key":
        PARLAY_API_KEY

}

try:

    response = requests.get(

        f"{BASE_URL}/sports",

        headers=headers,

        timeout=15

    )

    if response.status_code != 200:

        return []

    sports = response.json()

    output = []

    for sport in sports:

        key = sport.get(
            "key",
            ""
        )

        if key.startswith(
            "soccer_"
        ):

            output.append({

                "key":
                    key,

                "title":
                    sport.get(
                        "title",
                        key
                    )

            })

    return output

except Exception as e:

    print(
        "[SPORT ERROR]",
        str(e)
    )

    return []
```

def fetch_live_matches():

```
headers = {

    "X-API-Key":
        PARLAY_API_KEY

}

all_matches = []

sports = get_active_soccer_sports()

for sport in sports:

    try:

        url = (
            f"{BASE_URL}"
            f"/sports/"
            f"{sport['key']}"
            f"/live/points"
        )

        response = requests.get(

            url,

            headers=headers,

            timeout=10

        )

        if response.status_code == 200:

            data = response.json()

            if isinstance(
                data,
                list
            ):

                for item in data:

                    item["_league"] = (
                        sport["title"]
                    )

                    all_matches.append(
                        item
                    )

    except Exception as e:

        print(
            "[LIVE ERROR]",
            sport["key"],
            str(e)
        )

return all_matches



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
            False,

        "exhaustionScore":
            0,

        "fakeSteam":
            False,

        "continuationProbability":
            0,

        "divergence":
            "SYNC",

        "pressureScore":
            0,

        "aiWarning":
            "NORMAL"

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
# ADVANCED AI
# =========================

def calculate_exhaustion(history):

    if len(history) < 8:
        return 0

    recent = history[-8:]

    movement = max(recent) - min(recent)

    volatility = sum([

        abs(
            recent[i] -
            recent[i - 1]
        )

        for i in range(1, len(recent))

    ])

    exhaustion = min(

        100,

        int(
            volatility * 120 -
            movement * 40
        )

    )

    return max(0, exhaustion)

def detect_fake_steam(
    velocity,
    sync,
    arb
):

    if (
        velocity >= 5 and
        sync == 0 and
        arb < 2
    ):

        return True

    return False

def continuation_probability(
    velocity,
    sync,
    confidence
):

    score = int(

        velocity * 8 +

        sync * 25 +

        confidence * 0.6

    )

    return min(99, score)

def divergence_engine(
    move_a,
    move_b
):

    if move_a > 0 and move_b < 0:
        return "BOOK_DIVERGENCE"

    if move_a < 0 and move_b > 0:
        return "BOOK_DIVERGENCE"

    return "SYNC"

def sustained_pressure(
    history
):

    if len(history) < 10:
        return 0

    recent = history[-10:]

    avg = sum(recent) / len(recent)

    pressure = int(

        abs(
            recent[-1] - avg
        ) * 120

    )

    return min(99, pressure)

# =========================
# BUILD MARKET
# =========================

def build_market():
def build_market():

```
matches = fetch_live_matches()

output = []

for item in matches:

    try:

        home = item.get(
            "home_team",
            ""
        )

        away = item.get(
            "away_team",
            ""
        )

        minute = item.get(
            "minute",
            0
        )

        odd_a = round(
            random.uniform(
                0.88,
                1.02
            ),
            2
        )

        odd_b = round(
            random.uniform(
                0.88,
                1.02
            ),
            2
        )

        output.append({

            "match":
                f"{home} vs {away}",

            "league":
                item.get(
                    "_league",
                    "SOCCER"
                ),

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

            "clock":
                f"{minute}'",

            "liveStatus":
                "LIVE",

            "homeScore":
                item.get(
                    "home_score",
                    0
                ),

            "awayScore":
                item.get(
                    "away_score",
                    0
                )

        })

    except Exception as e:

        print(
            "[MAP ERROR]",
            str(e)
        )

return output
```

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

        exhaustion = calculate_exhaustion(
            market["movementHistory"]
        )

        fakeSteam = detect_fake_steam(

            velocity,
            sync,
            arb

        )

        continuation = continuation_probability(

            velocity,
            sync,
            confidence

        )

        divergence = divergence_engine(

            move_a,
            move_b

        )

        pressure = sustained_pressure(

            market["movementHistory"]
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
                trend,

            "exhaustion":
                exhaustion,

            "continuation":
                continuation,

            "pressure":
                pressure

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

        market["exhaustionScore"] = exhaustion

        market["fakeSteam"] = fakeSteam

        market["continuationProbability"] = continuation

        market["divergence"] = divergence

        market["pressureScore"] = pressure

        if exhaustion >= 70:

            market["aiWarning"] = "EXHAUSTION"

        elif fakeSteam:

            market["aiWarning"] = "FAKE_STEAM"

        elif continuation >= 80:

            market["aiWarning"] = "CONTINUATION"

        else:

            market["aiWarning"] = "NORMAL"

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
            "ADVANCED AI INTELLIGENCE ENGINE",

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
            exhaustion,
            continuation,
            pressure,
            divergence,
            fake_steam,
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

            "exhaustion":
                row[10],

            "continuation":
                row[11],

            "pressure":
                row[12],

            "divergence":
                row[13],

            "fakeSteam":
                bool(row[14]),

            "created":
                row[15]

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
            "advanced ai active"

    })

# =========================
# START
# =========================

if __name__ == "__main__":

    init_db()

    print("")
    print("===================================")
    print(" ADVANCED AI INTELLIGENCE ENGINE ")
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

