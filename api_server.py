from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
import threading
import time
import random
import os

app = Flask(__name__)

CORS(app)

socketio = SocketIO(
    app,
    cors_allowed_origins="*"
)

steam_data = []
logs = []

@app.route("/")
def home():

    return jsonify({

        "status": "online",

        "service": "OddsSeokeo API"

    })

@app.route("/steam")
def steam():

    return jsonify(steam_data)

def realtime_loop():

    global steam_data
    global logs

    while True:

        steam_data = [

            {

                "home_team": "PSG",

                "away_team": "Marseille",

                "market": "TAI/XIU",

                "line": "2.5",

                "odds": round(
                    random.uniform(
                        0.8,
                        1.2
                    ),
                    2
                ),

                "move": "+0.05",

                "direction": "UP",

                "bookmaker": "SBOBET"

            },

            {

                "home_team": "Barcelona",

                "away_team": "Real Madrid",

                "market": "TAI/XIU",

                "line": "3.0",

                "odds": round(
                    random.uniform(
                        0.8,
                        1.2
                    ),
                    2
                ),

                "move": "-0.04",

                "direction": "DOWN",

                "bookmaker": "SABA"

            }

        ]

        logs.insert(
            0,
            "Realtime odds updated"
        )

        logs = logs[:10]

        socketio.emit(
            "steam_update",
            steam_data
        )

        socketio.emit(
            "activity_logs",
            logs
        )

        time.sleep(3)

threading.Thread(
    target=realtime_loop,
    daemon=True
).start()

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5001
        )
    )

    socketio.run(
        app,
        host="0.0.0.0",
        port=port
    )