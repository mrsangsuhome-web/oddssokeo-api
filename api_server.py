from flask import Flask, jsonify
from flask_cors import CORS

import os
import time

app = Flask(__name__)

CORS(app)

# =========================================
# ROOT
# =========================================

@app.route("/")
def home():

    return jsonify({

        "service": "Asian Market Scanner",

        "status": "online"

    })

# =========================================
# MATCHES
# =========================================

@app.route("/matches")
def matches():

    matches = [

        {
            "league": "China U20 League",

            "match": "Shandong U20 vs Shaanxi Union U20",

            "open_ah": "-0.25",

            "curr_ah": "-0.75",

            "open_odds": 2.009,

            "curr_odds": 1.934,
        },

        {
            "league": "China U20 League",

            "match": "Shanghai Port U20 vs Beijing Guoan U20",

            "open_ah": "+0.25",

            "curr_ah": "-0.5",

            "open_odds": 1.884,

            "curr_odds": 1.793,
        },

        {
            "league": "International Friendly U20",

            "match": "Turkmenistan U20 vs Uzbekistan U20",

            "open_ah": "+1.25",

            "curr_ah": "+1.5",

            "open_odds": 1.862,

            "curr_odds": 1.925,
        },

        {
            "league": "Australia FFA Cup",

            "match": "Rochedale Rovers FC vs Capalaba FC",

            "open_ah": "-1.75",

            "curr_ah": "-2.25",

            "open_odds": 1.746,

            "curr_odds": 1.813,
        }

    ]

    data = []

    for item in matches:

        open_odds = item["open_odds"]

        curr_odds = item["curr_odds"]

        pi = round(
            curr_odds - open_odds,
            2
        )

        trend = "↑" if pi > 0 else "↓"

        row = {

            "league": item["league"],

            "match": item["match"],

            "open_ah": item["open_ah"],

            "curr_ah": item["curr_ah"],

            "open_odds": round(open_odds, 3),

            "curr_odds": f"{curr_odds:.3f}{trend}",

            "pi": f"{pi:+.2f}"

        }

        data.append(row)

    return jsonify(data)

# =========================================
# HEALTH
# =========================================

@app.route("/health")
def health():

    return jsonify({

        "status": "healthy",

        "time": int(time.time())

    })

# =========================================
# RUN
# =========================================

if __name__ == "__main__":

    port = int(
        os.environ.get("PORT", 10000)
    )

    app.run(
        host="0.0.0.0",
        port=port
    )