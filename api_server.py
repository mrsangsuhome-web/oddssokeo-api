from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
import random
import threading
import time

app = Flask(__name__)

CORS(app)

socketio = SocketIO(
    app,
    cors_allowed_origins="*"
)

steam_data = []
activity_logs = []

@app.route('/steam')
def steam():
    return jsonify(steam_data)

def generate_live_data():

    global steam_data
    global activity_logs

    matches = [

        {
            "home_team": "PSG",
            "away_team": "Marseille",
            "odds": 0.98,
            "previous_odds": 0.92,
            "line": "3.5",
            "move": "+0.06",
            "direction": "UP",
            "market": "TAI/XIU",
            "bookmaker": "SBOBET",
            "match_time": "72'",
            "steam_level": "HIGH"
        },

        {
            "home_team": "Barcelona",
            "away_team": "Real Madrid",
            "odds": 1.02,
            "previous_odds": 1.08,
            "line": "2.5",
            "move": "-0.06",
            "direction": "DOWN",
            "market": "TAI/XIU",
            "bookmaker": "SABA",
            "match_time": "55'",
            "steam_level": "MEDIUM"
        }

    ]

    while True:

        for match in matches:

            match["previous_odds"] = match["odds"]

            new_odds = round(
                random.uniform(0.80, 1.20),
                2
            )

            match["odds"] = new_odds

            diff = round(
                new_odds -
                match["previous_odds"],
                2
            )

            if diff >= 0:

                match["direction"] = "UP"

                match["move"] = f"+{diff}"

            else:

                match["direction"] = "DOWN"

                match["move"] = f"{diff}"

            log = (
                f"{match['home_team']} updated to {match['odds']}"
            )

            activity_logs.insert(0, log)

        activity_logs = activity_logs[:10]

        steam_data = matches

        socketio.emit(
            "steam_update",
            steam_data
        )

        socketio.emit(
            "activity_logs",
            activity_logs
        )

        time.sleep(3)

threading.Thread(
    target=generate_live_data,
    daemon=True
).start()

import os

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