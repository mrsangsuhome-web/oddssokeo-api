
from flask import Flask, jsonify
from flask_socketio import SocketIO

import requests
import time
import random

from threading import Thread
from datetime import datetime

app = Flask(__name__)

socketio = SocketIO(

    app,

    cors_allowed_origins="*",

    async_mode="threading"

)

API_URL = "https://oddssokeo-api-1.onrender.com/matches"

last_snapshot = []

connected_clients = 0


@app.route("/")
def home():

    return jsonify({

        "status": "websocket running",

        "clients": connected_clients,

        "server_time":
            datetime.now().strftime(
                "%H:%M:%S"
            )

    })


@app.route("/health")
def health():

    return jsonify({

        "status": "healthy",

        "websocket": True,

        "clients": connected_clients

    })


def generate_updates():

    global last_snapshot

    while True:

        try:

            response = requests.get(

                API_URL,

                timeout=10

            )

            data = response.json()

            updates = []

            for match in data[:60]:

                updates.append({

                    "match":
                        match.get("match"),

                    "league":
                        match.get("league"),

                    "leagueName":
                        match.get("leagueName"),

                    "heat":
                        match.get("heatLevel"),

                    "arb":
                        match.get("arbPercent"),

                    "score":

                        f"{match.get('homeScore')}:{match.get('awayScore')}"

                        if match.get("homeScore") is not None

                        else "-",

                    "clock":
                        match.get("clock"),

                    "status":
                        match.get("liveStatus"),

                    "bookA":
                        match.get("bookA"),

                    "bookB":
                        match.get("bookB"),

                    "oddA":
                        match.get("awayOddA"),

                    "oddB":
                        match.get("awayOddB"),

                    "movement":
                        match.get("movementDelta"),

                    "marketDepth":
                        match.get("marketDepth"),

                    "heatLevel":
                        match.get("heatLevel")

                })

            socketio.emit(

                "market_update",

                {

                    "markets": updates,

                    "updated":
                        datetime.now().strftime(
                            "%H:%M:%S"
                        )

                }

            )

            # LIVE TICKER

            if len(updates) > 0:

                hot_match = random.choice(
                    updates
                )

                ticker_message = (

                    f"{hot_match['match']} | "

                    f"{hot_match['arb']}% arb | "

                    f"{hot_match['heat']} movement"

                )

                socketio.emit(

                    "live_ticker",

                    {

                        "message":
                            ticker_message,

                        "time":
                            datetime.now().strftime(
                                "%H:%M:%S"
                            )

                    }

                )

            # HOT ALERTS

            hot_markets = [

                x for x in updates

                if x["heat"] == "HOT"

            ]

            if len(hot_markets) > 0:

                socketio.emit(

                    "hot_update",

                    {

                        "count":
                            len(hot_markets),

                        "markets":
                            hot_markets[:5]

                    }

                )

            # ARB ALERTS

            arb_markets = [

                x for x in updates

                if x["arb"] >= 2

            ]

            if len(arb_markets) > 0:

                socketio.emit(

                    "arb_update",

                    {

                        "count":
                            len(arb_markets),

                        "markets":
                            arb_markets[:10]

                    }

                )

            # HEARTBEAT

            socketio.emit(

                "heartbeat",

                {

                    "server_time":
                        datetime.now().strftime(
                            "%H:%M:%S"
                        ),

                    "markets":
                        len(updates)

                }

            )

            last_snapshot = updates

        except Exception as e:

            socketio.emit(

                "server_error",

                {

                    "error":
                        str(e)

                }

            )

        time.sleep(2)


@socketio.on("connect")
def handle_connect():

    global connected_clients

    connected_clients += 1

    socketio.emit(

        "connected",

        {

            "status": "LIVE",

            "clients":
                connected_clients

        }

    )

    print(

        f"[WS] Client connected | "

        f"total={connected_clients}"

    )


@socketio.on("disconnect")
def handle_disconnect():

    global connected_clients

    connected_clients -= 1

    if connected_clients < 0:

        connected_clients = 0

    print(

        f"[WS] Client disconnected | "

        f"total={connected_clients}"

    )


def websocket_loop():

    while True:

        try:

            generate_updates()

        except Exception as e:

            print(

                "[WS LOOP ERROR]",

                str(e)

            )

        time.sleep(1)


if __name__ == "__main__":

    print("")
    print("===================================")
    print(" PREMIUM ASIAN WS TERMINAL ")
    print("===================================")
    print(" WS PORT : 10001")
    print(" MODE    : THREADING")
    print("===================================")
    print("")

    Thread(

        target=websocket_loop,

        daemon=True

    ).start()

    socketio.run(

        app,

        host="0.0.0.0",

        port=10001,

        allow_unsafe_werkzeug=True

    )

