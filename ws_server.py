
from flask import Flask
from flask_socketio import SocketIO

import requests
import time
import random

from threading import Thread

app = Flask(__name__)

socketio = SocketIO(
    app,
    cors_allowed_origins="*"
)

API_URL = "https://oddssokeo-api-1.onrender.com/matches"

last_snapshot = []


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

            for match in data[:25]:

                updates.append({

                    "match":
                        match.get("match"),

                    "league":
                        match.get("league"),

                    "heat":
                        match.get("heatLevel"),

                    "arb":
                        match.get("arbPercent"),

                    "score":
                        f"{match.get('homeScore')}:{match.get('awayScore')}",

                    "clock":
                        match.get("clock"),

                    "bookA":
                        match.get("bookA"),

                    "bookB":
                        match.get("bookB"),

                    "oddA":
                        match.get("awayOddA"),

                    "oddB":
                        match.get("awayOddB")

                })

            socketio.emit(
                "market_update",
                updates
            )

            if len(updates) > 0:

                random_match = random.choice(
                    updates
                )

                socketio.emit(
                    "live_ticker",
                    {

                        "message":
                            f"{random_match['match']} "
                            f"{random_match['arb']}% arb"

                    }
                )

            last_snapshot = updates

        except Exception as e:

            socketio.emit(
                "server_error",
                {
                    "error": str(e)
                }
            )

        time.sleep(2)


@socketio.on("connect")
def handle_connect():

    socketio.emit(
        "connected",
        {
            "status": "LIVE"
        }
    )


if __name__ == "__main__":

    Thread(
        target=generate_updates,
        daemon=True
    ).start()

    socketio.run(
        app,
        host="0.0.0.0",
        port=10001
    )
