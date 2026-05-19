from flask import Flask, jsonify
from flask_cors import CORS
import random
import time

app = Flask(__name__)

CORS(app)

# ROOT

@app.route("/")
def home():

    return jsonify({
        "service": "Sports Intelligence API",
        "status": "online"
    })

# STATS API

@app.route("/stats")
def stats():

    return jsonify({

        "latency": random.randint(20, 90),

        "online_users": random.randint(5, 20),

        "activity_alerts": random.randint(1, 10),

        "matches": random.randint(20, 50),

    })

# MATCHES API

@app.route("/matches")
def matches():

    data = [

        {
            "home_team": "PSG",
            "away_team": "Marseille",
            "status": "LIVE",
            "minute": random.randint(1, 90),
            "pressure": random.randint(50, 100),
            "tempo": random.choice([
                "FAST",
                "NORMAL",
                "SLOW"
            ]),
            "momentum": random.choice([
                "HOME",
                "AWAY",
                "BALANCED"
            ]),
            "velocity": random.randint(40, 100),
            "activity_level": random.choice([
                "LOW",
                "MEDIUM",
                "HIGH",
                "EXTREME"
            ]),
            "kickoff_in": 0
        },

        {
            "home_team": "Barcelona",
            "away_team": "Real Madrid",
            "status": "LIVE",
            "minute": random.randint(1, 90),
            "pressure": random.randint(50, 100),
            "tempo": random.choice([
                "FAST",
                "NORMAL",
                "SLOW"
            ]),
            "momentum": random.choice([
                "HOME",
                "AWAY",
                "BALANCED"
            ]),
            "velocity": random.randint(40, 100),
            "activity_level": random.choice([
                "LOW",
                "MEDIUM",
                "HIGH",
                "EXTREME"
            ]),
            "kickoff_in": 0
        },

        {
            "home_team": "Liverpool",
            "away_team": "Manchester City",
            "status": "LIVE",
            "minute": random.randint(1, 90),
            "pressure": random.randint(50, 100),
            "tempo": random.choice([
                "FAST",
                "NORMAL",
                "SLOW"
            ]),
            "momentum": random.choice([
                "HOME",
                "AWAY",
                "BALANCED"
            ]),
            "velocity": random.randint(40, 100),
            "activity_level": random.choice([
                "LOW",
                "MEDIUM",
                "HIGH",
                "EXTREME"
            ]),
            "kickoff_in": 0
        },

        {
            "home_team": "Bayern",
            "away_team": "Dortmund",
            "status": "LIVE",
            "minute": random.randint(1, 90),
            "pressure": random.randint(50, 100),
            "tempo": random.choice([
                "FAST",
                "NORMAL",
                "SLOW"
            ]),
            "momentum": random.choice([
                "HOME",
                "AWAY",
                "BALANCED"
            ]),
            "velocity": random.randint(40, 100),
            "activity_level": random.choice([
                "LOW",
                "MEDIUM",
                "HIGH",
                "EXTREME"
            ]),
            "kickoff_in": 0
        }

    ]

    return jsonify(data)

# HEALTH CHECK

@app.route("/health")
def health():

    return jsonify({
        "status": "healthy",
        "time": int(time.time())
    })

# RUN SERVER

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=10000
    )