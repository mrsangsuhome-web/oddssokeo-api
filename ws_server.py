
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

import random
import time
import threading

app = Flask(__name__)

CORS(app)

socketio = SocketIO(

    app,

    cors_allowed_origins="*",

    async_mode="threading",

    ping_timeout=20,

    ping_interval=10

)

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

    "PSG vs Arsenal",
    "Manchester City vs Aston Villa",
    "Liverpool vs Brentford",
    "Tottenham vs Everton",
    "Napoli vs Udinese",
    "AC Milan vs Cagliari",
    "Torino vs Juventus",
    "Villarreal vs Atletico Madrid",
    "Saint-Étienne vs Nice",
    "Paderborn vs Wolfsburg"

]

MARKET_MEMORY = {}

CLIENTS = 0

def create_market(match):

    if match not in MARKET_MEMORY:

        MARKET_MEMORY[match] = {

            "oddA":
                round(
                    random.uniform(0.84, 1.02),
                    2
                ),

            "oddB":
                round(
                    random.uniform(0.84, 1.02),
                    2
                ),

            "trend":
                "BALANCED"

        }

    market = MARKET_MEMORY[match]

    move_a = random.choice([
        -0.03,
        -0.02,
        -0.01,
        0,
        0.01,
        0.02,
        0.03
    ])

    move_b = random.choice([
        -0.03,
        -0.02,
        -0.01,
        0,
        0.01,
        0.02,
        0.03
    ])

    market["oddA"] = round(
        market["oddA"] + move_a,
        2
    )

    market["oddB"] = round(
        market["oddB"] + move_b,
        2
    )

    market["oddA"] = max(
        0.75,
        min(1.15, market["oddA"])
    )

    market["oddB"] = max(
        0.75,
        min(1.15, market["oddB"])
    )

    velocity = round(

        abs(move_a) * 100 +

        abs(move_b) * 100,

        2

    )

    arb = round(

        abs(
            market["oddA"] -
            market["oddB"]
        ) * 100,

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

    if market["trend"] != trend:

        if market["trend"] != "BALANCED":

            reversal = True

    market["trend"] = trend

    confidence = min(

        99,

        int(
            velocity * 8 +
            arb * 8 +
            sync * 15
        )

    )

    return {

        "match":
            match,

        "bookA":
            random.choice(
                BOOKMAKERS
            ),

        "bookB":
            random.choice(
                BOOKMAKERS
            ),

        "awayOddA":
            market["oddA"],

        "awayOddB":
            market["oddB"],

        "marketVelocity":
            velocity,

        "arbPercent":
            arb,

        "syncLevel":
            sync,

        "steamMove":
            steam,

        "sharpMoney":
            sharp,

        "cluster":
            cluster,

        "trend":
            trend,

        "trendReversal":
            reversal,

        "aiConfidence":
            confidence,

        "time":
            time.strftime("%H:%M:%S")

    }

@app.route("/")
def home():

    return {

        "status":
            "LIVE",

        "engine":
            "TRUE WEBSOCKET INTELLIGENCE STREAM",

        "clients":
            CLIENTS

    }

@socketio.on("connect")
def connect():

    global CLIENTS

    CLIENTS += 1

    print(
        f"CLIENT CONNECTED ({CLIENTS})"
    )

    socketio.emit(

        "system",

        {

            "message":
                "CONNECTED TO INTELLIGENCE STREAM",

            "time":
                time.strftime("%H:%M:%S")

        }

    )

@socketio.on("disconnect")
def disconnect():

    global CLIENTS

    CLIENTS -= 1

    if CLIENTS < 0:
        CLIENTS = 0

    print(
        f"CLIENT DISCONNECTED ({CLIENTS})"
    )

def heartbeat_loop():

    while True:

        socketio.emit(

            "heartbeat",

            {

                "status":
                    "alive",

                "time":
                    time.strftime("%H:%M:%S")

            }

        )

        time.sleep(10)

def intelligence_stream_loop():

    while True:

        batch = []

        for _ in range(5):

            market = create_market(
                random.choice(MATCHES)
            )

            batch.append(market)

            socketio.emit(

                "intelligence_stream",

                market

            )

            socketio.emit(

                "replay_stream",

                {

                    "match":
                        market["match"],

                    "velocity":
                        market["marketVelocity"],

                    "trend":
                        market["trend"],

                    "confidence":
                        market["aiConfidence"]

                }

            )

            if market["cluster"] != "NORMAL":

                socketio.emit(

                    "cluster_alert",

                    {

                        "match":
                            market["match"],

                        "cluster":
                            market["cluster"],

                        "confidence":
                            market["aiConfidence"]

                    }

                )

            if market["trendReversal"]:

                socketio.emit(

                    "reversal_alert",

                    {

                        "match":
                            market["match"],

                        "trend":
                            market["trend"]

                    }

                )

            if market["aiConfidence"] >= 75:

                socketio.emit(

                    "ai_signal",

                    {

                        "match":
                            market["match"],

                        "confidence":
                            market["aiConfidence"],

                        "cluster":
                            market["cluster"]

                    }

                )

            socketio.emit(

                "console",

                {

                    "time":
                        market["time"],

                    "message":
                        f'{market["match"]} {market["cluster"]} AI {market["aiConfidence"]}%'

                }

            )

        socketio.emit(

            "market_batch",

            batch

        )

        time.sleep(2)

if __name__ == "__main__":

    threading.Thread(

        target=heartbeat_loop,

        daemon=True

    ).start()

    threading.Thread(

        target=intelligence_stream_loop,

        daemon=True

    ).start()

    print("")
    print("===================================")
    print(" TRUE INTELLIGENCE STREAM ")
    print("===================================")
    print(" WS PORT : 10001")
    print("===================================")
    print("")

    socketio.run(

        app,

        host="0.0.0.0",

        port=10001,

        debug=True,

        allow_unsafe_werkzeug=True

    )

