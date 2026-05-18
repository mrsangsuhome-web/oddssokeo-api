```python id="backend-complete-terminal-final"
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

SECRET_KEY = "oddssokeo_vip_secret"

steam_data = []

steam_alerts = []

system_stats = {

    "latency": 42,

    "online_users": 12,

    "steam_alerts": 5,

    "feed_status": "LIVE",

    "matches": 28

}

USERS = {

    "admin": {

        "password": "123456",

        "vip": True

    }

}

@app.route("/")
def home():

    return jsonify({

        "service": "OddsSeokeo API",

        "status": "online"

    })

@app.route("/login", methods=["POST"])
def login():

    data = request.json

    username = data.get("username")

    password = data.get("password")

    user = USERS.get(username)

    if not user:

        return jsonify({

            "error": "User not found"

        }), 401

    if user["password"] != password:

        return jsonify({

            "error": "Wrong password"

        }), 401

    token = jwt.encode({

        "username": username,

        "vip": True,

        "exp":

            datetime.datetime.utcnow()

            + datetime.timedelta(days=30)

    },

    SECRET_KEY,

    algorithm="HS256")

    return jsonify({

        "token": token,

        "vip": True

    })

def verify_token(req):

    auth = req.headers.get(

        "Authorization"

    )

    if not auth:

        return None

    try:

        token = auth.split(" ")[1]

        decoded = jwt.decode(

            token,

            SECRET_KEY,

            algorithms=["HS256"]

        )

        return decoded

    except:

        return None

@app.route("/stats")
def stats():

    user = verify_token(request)

    if not user:

        return jsonify({

            "error": "Unauthorized"

        }), 401

    return jsonify(system_stats)

@app.route("/alerts")
def alerts():

    user = verify_token(request)

    if not user:

        return jsonify({

            "error": "Unauthorized"

        }), 401

    return jsonify(steam_alerts)

@app.route("/steam")
def steam():

    user = verify_token(request)

    if not user:

        return jsonify({

            "error": "Unauthorized"

        }), 401

    return jsonify(steam_data)

def random_level():

    return random.choice(

        [

            "LOW",

            "MEDIUM",

            "HIGH",

            "EXTREME"

        ]

    )

def realtime_loop():

    global steam_data

    while True:

        system_stats["latency"] = random.randint(25, 80)

        system_stats["online_users"] = random.randint(8, 26)

        system_stats["steam_alerts"] = random.randint(2, 12)

        system_stats["matches"] = random.randint(18, 52)

        steam_alerts.insert(

            0,

            {

                "match": "PSG vs Marseille",

                "alert": "HIGH STEAM",

                "book": "SBOBET",

                "move": "+0.12",

                "time":

                    datetime.datetime.now()

                    .strftime("%H:%M:%S")

            }

        )

        steam_alerts[:] = steam_alerts[:10]

        steam_data = [

            {

                "match": "PSG vs Marseille",

                "home_team": "PSG",

                "away_team": "Marseille",

                "status": "LIVE",

                "minute": random.randint(

                    12,

                    88

                ),

                "kickoff_in": 0,

                "market": "O/U 2.5",

                "line": "2.5",

                "odds": round(

                    random.uniform(

                        0.80,

                        1.20

                    ),

                    2

                ),

                "steam_level":

                    random_level(),

                "velocity":

                    random.randint(

                        40,

                        95

                    ),

                "lead_book": "SBOBET",

                "follow_book": "ISN",

                "follow_delay":

                    random.randint(

                        1,

                        8

                    ),

                "move": "+0.05"

            },

            {

                "match": "Barcelona vs Real Madrid",

                "home_team": "Barcelona",

                "away_team": "Real Madrid",

                "status":

                    "STARTING SOON",

                "minute": 0,

                "kickoff_in":

                    random.randint(

                        5,

                        28

                    ),

                "market": "O/U 3.0",

                "line": "3.0",

                "odds": round(

                    random.uniform(

                        0.80,

                        1.20

                    ),

                    2

                ),

                "steam_level":

                    random_level(),

                "velocity":

                    random.randint(

                        30,

                        90

                    ),

                "lead_book": "SABA",

                "follow_book": "KSPORT",

                "follow_delay":

                    random.randint(

                        1,

                        8

                    ),

                "move": "-0.04"

            }

        ]

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

    app.run(

        host="0.0.0.0",

        port=port

    )
```
