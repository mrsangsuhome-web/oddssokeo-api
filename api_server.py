from flask import Flask, jsonify, request
from flask_cors import CORS

import threading
import time
import random
import os
import jwt
import datetime

app = Flask(__name__)

CORS(app)

SECRET_KEY = "sports_intelligence_secret"

matches_data = []

system_stats = {
    "latency": 42,
    "online_users": 12,
    "activity_alerts": 5,
    "matches": 28
}

@app.route("/")
def home():

    return jsonify({
        "service": "Sports Intelligence API",
        "status": "online"
    })

@app.route("/stats")
def stats():

    return jsonify(system_stats)

@app.route("/matches")
def matches():

    return jsonify(matches_data)

def realtime_loop():

    global matches_data

    while True:

        system_stats["latency"] = random.randint(25, 80)

        system_stats["online_users"] = random.randint(8, 26)

        system_stats["activity_alerts"] = random.randint(2, 12)

        system_stats["matches"] = random.randint(18, 52)

        matches_data = [

            {
                "home_team": "PSG",
                "away_team": "Marseille",
                "status": "LIVE",
                "minute": random.randint(12, 88),
                "kickoff_in": 0,
                "velocity": random.randint(40, 95),
                "activity_level": random.choice([
                    "LOW",
                    "MEDIUM",
                    "HIGH",
                    "EXTREME"
                ]),
                "pressure": random.randint(40, 99),
                "tempo": random.choice([
                    "SLOW",
                    "NORMAL",
                    "FAST"
                ]),
                "momentum": random.choice([
                    "HOME",
                    "AWAY",
                    "BALANCED"
                ])
            }

        ]

        time.sleep(3)

threading.Thread(
    target=realtime_loop,
    daemon=True
).start()

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5001))

    app.run(
        host="0.0.0.0",
        port=port
    )