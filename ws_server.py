
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

import requests
import threading
import time

app = Flask(__name__)


CORS(
    app,
    resources={
        r"/*": {
            "origins": "*"
        }
    }
)





socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading",
    logger=True,
    engineio_logger=True



)

CLIENTS = 0

API_URL = (
    "https://oddssokeo-api-1.onrender.com/matches"
)


def get_live_markets():

    try:

        response = requests.get(
            API_URL,
            timeout=15
        )

        if response.status_code == 200:

            data = response.json()

            if isinstance(
                data,
                list
            ):
                return data

        return []

    except Exception as e:

        print(
            "[API ERROR]",
            str(e)
        )

        return []

def get_live_markets():

    try:

        response = requests.get(
            API_URL,
            timeout=10
        )

        if response.status_code == 200:

            return response.json()

        return []

    except Exception as e:

        print(
            "API ERROR:",
            str(e)
        )

        return []


@app.route("/")
def home():

    return {

        "status": "LIVE",

        "engine":
            "REALTIME MARKET SCANNER",

        "clients":
            CLIENTS

    }


@socketio.on("connect")
def connect():

    global CLIENTS

    CLIENTS += 1

    print(
        f"CLIENT CONNECTED ({CLIENTS})"
    )

    socketio.emit(

        "system",

        {

            "message":
                "CONNECTED TO REALTIME STREAM",

            "time":
                time.strftime("%H:%M:%S")

        }

    )


@socketio.on("disconnect")
def disconnect():

    global CLIENTS

    CLIENTS -= 1

    if CLIENTS < 0:
        CLIENTS = 0

    print(
        f"CLIENT DISCONNECTED ({CLIENTS})"
    )
def heartbeat_loop():

    while True:

        socketio.emit(

            "heartbeat",

            {

                "status": "alive",

                "time":
                    time.strftime("%H:%M:%S")

            }

        )

        time.sleep(10)


def intelligence_stream_loop():

    while True:

        try:

            markets = get_live_markets()

            socketio.emit(
                "market_batch",
                markets
            )

            socketio.emit(
                "source_status",
                {
                    "status": "ONLINE",
                    "markets": len(markets),
                    "clients": CLIENTS,
                    "time": time.strftime("%H:%M:%S")
                }
            )

            socketio.emit(
                "console",
                {
                    "time": time.strftime("%H:%M:%S"),
                    "message":
                        f"Markets: {len(markets)}"
                }
            )

        except Exception as e:

            print(
                "[WS ERROR]",
                str(e)
            )

        time.sleep(2)

        socketio.emit(

            "source_status",

            {

                "status": "ONLINE",

                "markets":
                    len(markets),

                "time":
                    time.strftime("%H:%M:%S")

            }

        )

        time.sleep(2)


if __name__ == "__main__":

    threading.Thread(
        target=heartbeat_loop,
        daemon=True
    ).start()

    threading.Thread(
        target=intelligence_stream_loop,
        daemon=True
    ).start()

    print("")
    print("===================================")
    print(" REALTIME MARKET SCANNER WS ")
    print("===================================")
    print(" WS PORT : 10001")
    print("===================================")
    print("")

    import os

    socketio.run(
        app,
        host="0.0.0.0",
        port=int(
            os.environ.get(
                "PORT",
                10001
            )
        ),
        debug=False,
        allow_unsafe_werkzeug=True
    )
