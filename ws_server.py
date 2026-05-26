
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

def generate_market(match):

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
                )

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

    if market["oddA"] < 0.75:
        market["oddA"] = 0.75

    if market["oddA"] > 1.15:
        market["oddA"] = 1.15

    if market["oddB"] < 0.75:
        market["oddB"] = 0.75

    if market["oddB"] > 1.15:
        market["oddB"] = 1.15

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

    steam = velocity >= 5

    sharp = arb >= 4

    heat = "NORMAL"

    if steam:
        heat = "STEAM"

    elif sharp:
        heat = "SHARP"

    elif velocity >= 3:
        heat = "HOT"

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

        "arbPercent":
            arb,

        "marketVelocity":
            velocity,

        "heatLevel":
            heat,

        "steamMove":
            steam,

        "sharpMoney":
            sharp,

        "signalStrength":
            min(
                100,
                int(
                    velocity * 10 +
                    arb * 10
                )
            ),

        "created":
            int(time.time())

    }

@app.route("/")
def home():

    return {

        "status":
            "running",

        "engine":
            "true realtime push engine",

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

            "type":
                "SYSTEM",

            "message":
                "CONNECTED TO REALTIME TERMINAL",

            "time":
                int(time.time())

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
                    int(time.time())

            }

        )

        time.sleep(10)

def market_stream_loop():

    while True:

        batch = []

        for _ in range(4):

            market = generate_market(
                random.choice(MATCHES)
            )

            batch.append(market)

            if market["arbPercent"] >= 3:

                socketio.emit(

                    "arb_alert",

                    {

                        "priority":
                            "HIGH",

                        "match":
                            market["match"],

                        "arbPercent":
                            market["arbPercent"]

                    }

                )

            if market["steamMove"]:

                socketio.emit(

                    "steam_alert",

                    {

                        "priority":
                            "HIGH",

                        "match":
                            market["match"],

                        "velocity":
                            market["marketVelocity"]

                    }

                )

            if market["sharpMoney"]:

                socketio.emit(

                    "sharp_alert",

                    {

                        "priority":
                            "MEDIUM",

                        "match":
                            market["match"],

                        "arb":
                            market["arbPercent"]

                    }

                )

            if market["marketVelocity"] >= 5:

                socketio.emit(

                    "velocity_alert",

                    {

                        "priority":
                            "HIGH",

                        "match":
                            market["match"],

                        "velocity":
                            market["marketVelocity"]

                    }

                )

            socketio.emit(

                "console",

                {

                    "time":
                        time.strftime("%H:%M:%S"),

                    "message":
                        f'{market["match"]} {market["heatLevel"]} {market["arbPercent"]}%'

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

        target=market_stream_loop,

        daemon=True

    ).start()

    print("")
    print("===================================")
    print(" TRUE REALTIME PUSH ENGINE ")
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

