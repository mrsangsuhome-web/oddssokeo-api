
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

import random
import time

app = Flask(__name__)

CORS(app)

socketio = SocketIO(

    app,

    cors_allowed_origins="*",

    async_mode="threading"

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

def build_market():

    arb = round(
        random.uniform(0.5, 5.4),
        2
    )

    heat = random.choice([
        "NORMAL",
        "HOT",
        "SHARP",
        "STEAM"
    ])

    velocity = round(
        random.uniform(0.4, 6.5),
        2
    )

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
            random.choice(
                MATCHES
            ),

        "arbPercent":
            arb,

        "heatLevel":
            heat,

        "bookA":
            random.choice(
                BOOKMAKERS
            ),

        "bookB":
            random.choice(
                BOOKMAKERS
            ),

        "marketVelocity":
            velocity,

        "sharpMoney":
            sharp_money,

        "steamMove":
            steam_move,

        "workflowTriggers": [

            random.choice([
                "LIVE_ARB",
                "STEAM_MOVE",
                "HOT_MOVEMENT",
                "SHARP_ACTION"
            ]),

            random.choice([
                "VALUE_BET",
                "PRIORITY_ALERT",
                "MOMENTUM_SPIKE"
            ])

        ],

        "signalStrength":
            random.randint(40, 100),

        "created":
            int(time.time())

    }

@app.route("/")
def home():

    return {

        "status":
            "websocket running",

        "engine":
            "premium sportsbook realtime feed"

    }

@socketio.on("connect")
def handle_connect():

    print("CLIENT CONNECTED")

    socketio.emit(

        "system",

        {

            "message":
                "CONNECTED TO PREMIUM TERMINAL",

            "time":
                int(time.time())

        }

    )

@socketio.on("disconnect")
def handle_disconnect():

    print("CLIENT DISCONNECTED")

def broadcast_loop():

    while True:

        market = build_market()

        socketio.emit(

            "market_update",

            market

        )

        if market["arbPercent"] >= 3:

            socketio.emit(

                "live_alert",

                {

                    "type":
                        "ARB",

                    "message":
                        f'{market["match"]} ARB {market["arbPercent"]}%',

                    "priority":
                        "HIGH"

                }

            )

        if market["sharpMoney"]:

            socketio.emit(

                "live_alert",

                {

                    "type":
                        "SHARP",

                    "message":
                        f'{market["match"]} sharp money detected',

                    "priority":
                        "MEDIUM"

                }

            )

        if market["steamMove"]:

            socketio.emit(

                "live_alert",

                {

                    "type":
                        "STEAM",

                    "message":
                        f'{market["match"]} steam move detected',

                    "priority":
                        "HIGH"

                }

            )

        if market["marketVelocity"] >= 5:

            socketio.emit(

                "live_alert",

                {

                    "type":
                        "VELOCITY",

                    "message":
                        f'{market["match"]} velocity spike',

                    "priority":
                        "HIGH"

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

        time.sleep(2)

if __name__ == "__main__":

    socketio.start_background_task(
        broadcast_loop
    )

    print("")
    print("===================================")
    print(" PREMIUM TERMINAL WS ")
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

