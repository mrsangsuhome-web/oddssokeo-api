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

activity_alerts = []

history_data = []

system_stats = {

```
"latency": 42,

"online_users": 12,

"activity_alerts": 5,

"feed_status": "LIVE",

"matches": 28
```

}

USERS = {

```
"admin": {

    "password": "123456",

    "vip": True

}
```

}

@app.route("/")
def home():

```
return jsonify({

    "service": "Sports Intelligence API",

    "status": "online"

})
```

@app.route("/login", methods=["POST"])
def login():

```
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
```

def verify_token(req):

```
auth = req.headers.get("Authorization")

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
```

@app.route("/stats")
def stats():

```
user = verify_token(request)

if not user:

    return jsonify({

        "error": "Unauthorized"

    }), 401

return jsonify(system_stats)
```

@app.route("/alerts")
def alerts():

```
user = verify_token(request)

if not user:

    return jsonify({

        "error": "Unauthorized"

    }), 401

return jsonify(activity_alerts)
```

@app.route("/matches")
def matches():

```
user = verify_token(request)

if not user:

    return jsonify({

        "error": "Unauthorized"

    }), 401

return jsonify(matches_data)
```

@app.route("/console")
def console():

```
user = verify_token(request)

if not user:

    return jsonify({

        "error": "Unauthorized"

    }), 401

logs = [

    "[17:42:12] MOMENTUM SPIKE DETECTED",

    "[17:42:15] HIGH PRESSURE ACTIVE",

    "[17:42:18] LIVE EVENT CLUSTER",

    "[17:42:22] MATCH INTENSITY INCREASE",

    "[17:42:25] ANALYTICS ENGINE RUNNING"

]

return jsonify(logs)
```

@app.route("/history")
def history():

```
user = verify_token(request)

if not user:

    return jsonify({

        "error": "Unauthorized"

    }), 401

return jsonify(history_data[:20])
```

def realtime_loop():

```
global matches_data

while True:

    system_stats["latency"] = random.randint(25, 80)

    system_stats["online_users"] = random.randint(8, 26)

    system_stats["activity_alerts"] = random.randint(2, 12)

    system_stats["matches"] = random.randint(18, 52)

    activity_alerts.insert(

        0,

        {

            "match": "PSG vs Marseille",

            "alert": "HIGH MOMENTUM",

            "source": "LIVE ENGINE",

            "activity": "+0.12",

            "time":
                datetime.datetime.now()
                .strftime("%H:%M:%S")

        }

    )

    activity_alerts[:] = activity_alerts[:10]

    matches_data = [

        {

            "match": "PSG vs Marseille",

            "home_team": "PSG",

            "away_team": "Marseille",

            "status": "LIVE",

            "minute": random.randint(12, 88),

            "kickoff_in": 0,

            "market": "INTENSITY",

            "line": "2.5",

            "velocity": random.randint(40, 95),

            "activity_level": random.choice(

                [

                    "LOW",

                    "MEDIUM",

                    "HIGH",

                    "EXTREME"

                ]

            ),

            "pressure": random.randint(40, 99),

            "tempo": random.choice(

                [

                    "SLOW",

                    "NORMAL",

                    "FAST"

                ]

            ),

            "momentum": random.choice(

                [

                    "HOME",

                    "AWAY",

                    "BALANCED"

                ]

            ),

            "intensity": random.choice(

                [

                    "LOW",

                    "MEDIUM",

                    "HIGH",

                    "EXTREME"

                ]

            ),

            "lead_source": "CORE FEED",

            "follow_source": "LIVE ENGINE",

            "follow_delay": random.randint(1, 8),

            "activity": "+0.05"

        },

        {

            "match": "Barcelona vs Real Madrid",

            "home_team": "Barcelona",

            "away_team": "Real Madrid",

            "status": "STARTING SOON",

            "minute": 0,

            "kickoff_in": random.randint(5, 28),

            "market": "PRESSURE",

            "line": "3.0",

            "velocity": random.randint(30, 90),

            "activity_level": random.choice(

                [

                    "LOW",

                    "MEDIUM",

                    "HIGH"

                ]

            ),

            "pressure": random.randint(40, 99),

            "tempo": random.choice(

                [

                    "SLOW",

                    "NORMAL",

                    "FAST"

                ]

            ),

            "momentum": random.choice(

                [

                    "HOME",

                    "AWAY",

                    "BALANCED"

                ]

            ),

            "intensity": random.choice(

                [

                    "LOW",

                    "MEDIUM",

                    "HIGH",

                    "EXTREME"

                ]

            ),

            "lead_source": "EVENT ENGINE",

            "follow_source": "TRACKER NODE",

            "follow_delay": random.randint(1, 8),

            "activity": "-0.04"

        }

    ]

    history_data.insert(

        0,

        {

            "time":
                datetime.datetime.now()
                .strftime("%H:%M:%S"),

            "matches": matches_data

        }

    )

    history_data[:] = history_data[:20]

    time.sleep(3)
```

threading.Thread(

```
target=realtime_loop,

daemon=True
```

).start()

if **name** == "**main**":

```
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
