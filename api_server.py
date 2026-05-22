from flask import Flask, jsonify, request
from flask_cors import CORS

import random
import time
import requests

app = Flask(__name__)

CORS(app)

BOT_TOKEN = "8925919932:AAE_CN7NRn9JCbtknc9RqwXdzc9xqfGpG6g"

CHAT_ID = "@sokeoscanner_bot"


SPORTS = [

    "ENGLISH_PREMIER_LEAGUE",

    "SPAIN_LA_LIGA",

    "ITALY_SERIE_A",

    "GERMANY_BUNDESLIGA",

    "FRANCE_LIGUE_ONE",

    "BELGIUM_FIRST_DIV",

    "USA_MLS",

    "PORTUGAL_PRIMEIRA_LIGA",

    "NETHERLANDS_EREDIVISIE",

    "TURKEY_SUPER_LIG",

    "SCOTLAND_PREMIERSHIP",

    "SWISS_SUPER_LEAGUE",

    "AUSTRIA_BUNDESLIGA",

    "DENMARK_SUPERLIGA",

    "NORWAY_ELITESERIEN",

    "SWEDEN_ALLSVENSKAN",

    "BRAZIL_SERIE_A",

    "ARGENTINA_PRIMERA",

    "MEXICO_LIGA_MX",

    "JAPAN_J_LEAGUE",

    "KOREA_K_LEAGUE",

    "CHINA_SUPER_LEAGUE",

    "AUSTRALIA_A_LEAGUE",

    "SAUDI_PRO_LEAGUE",

    "QATAR_STARS_LEAGUE",

    "UAE_PRO_LEAGUE",

    "UEFA_CHAMPIONS_LEAGUE",

    "UEFA_EUROPA_LEAGUE",

    "UEFA_CONFERENCE_LEAGUE",

    "FIFA_CLUB_WORLD_CUP"


]


BOOKMAKERS = [

    "SBO",

    "PIN",

    "IBC",

    "188",

    "CMD",

    "SABA",

    "BTI",

    "KSP",

    "ISN"

]


MATCHES = [

    ("Liverpool", "Arsenal"),

    ("Chelsea", "Manchester City"),

    ("Real Madrid", "Barcelona"),

    ("AC Milan", "Inter"),

    ("PSG", "Marseille"),

    ("Bayern", "Dortmund"),

    ("Juventus", "Napoli"),

    ("Atletico Madrid", "Sevilla"),

    ("Ajax", "PSV"),

    ("LA Galaxy", "Inter Miami")

]


def generate_live_time():

    status = random.choice([

        "H1",

        "H2",

        "HT",

        "PRE"

    ])

    if status == "PRE":

        return "PRE"

    if status == "HT":

        return "HT"

    minute = random.randint(1, 45)

    extra = random.randint(0, 4)

    if extra > 0:

        return f"{status} {minute}+{extra}'"

    return f"{status} {minute}'"


def generate_match():

    home, away = random.choice(MATCHES)

    market = random.choice([

        "FT O/U",

        "FT HDP"

    ])

    line = random.choice([

        "0.5",

        "1",

        "1.5",

        "2",

        "2.5",

        "2.5/3",

        "3"

    ])

    base = round(

        random.uniform(0.84, 0.96),

        2

    )

    gap = round(

        random.uniform(0.01, 0.06),

        2

    )

    awayA = round(base, 2)

    awayB = round(base + gap, 2)

    homeA = round(

        random.uniform(0.84, 0.96),

        2

    )

    homeB = round(

        random.uniform(0.84, 0.96),

        2

    )

    bookA, bookB = random.sample(

        BOOKMAKERS,

        2

    )

    return {

        "match": f"{home} vs {away}",

        "league": random.choice(SPORTS),

        "market": market,

        "line": line,

        "bookA": bookA,

        "bookB": bookB,

        "awayOddA": awayA,

        "awayOddB": awayB,

        "homeOddA": homeA,

        "homeOddB": homeB,

        "gap": gap,

        "live": True,

        "liveTime": generate_live_time(),

        "timestamp": int(time.time())

    }


@app.route("/")
def root():

    return jsonify({

        "status": "running",

        "matches": 20,

        "bookmakers": len(BOOKMAKERS)

    })


@app.route("/matches")
def matches():

    data = [

        generate_match()

        for _ in range(20)

    ]

    data = sorted(

        data,

        key=lambda x: x["gap"],

        reverse=True

    )

    return jsonify(data)


@app.route("/send_telegram", methods=["POST"])
def send_telegram():

    try:

        data = request.json

        message = data.get(

            "message",

            ""

        )

        if not message:

            return jsonify({

                "success": False,

                "error": "Empty message"

            })

        url = (
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        )

        payload = {

            "chat_id": CHAT_ID,

            "text": message

        }

        r = requests.post(

            url,

            json=payload,

            timeout=10

        )

        return jsonify({

            "success": True,

            "telegram": r.json()

        })

    except Exception as e:

        return jsonify({

            "success": False,

            "error": str(e)

        })


if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=10000

    )