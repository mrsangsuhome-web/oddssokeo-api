from flask import Flask, jsonify, request
from flask_cors import CORS

import random
import time
import requests

app = Flask(__name__)

CORS(app)

BOT_TOKEN = "from flask import Flask, jsonify, request
from flask_cors import CORS

import random
import time
import requests

app = Flask(__name__)

CORS(app)

BOT_TOKEN = "from flask import Flask, jsonify, request
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

    "ENGLISH_CHAMPIONSHIP",

    "SPAIN_LA_LIGA",

    "ITALY_SERIE_A",

    "GERMANY_BUNDESLIGA",

    "FRANCE_LIGUE_ONE",

    "BELGIUM_FIRST_DIV",

    "PORTUGAL_PRIMEIRA_LIGA",

    "NETHERLANDS_EREDIVISIE",

    "TURKEY_SUPER_LIG",

    "SCOTLAND_PREMIERSHIP",

    "BRAZIL_SERIE_A",

    "ARGENTINA_PRIMERA",

    "USA_MLS",

    "JAPAN_J_LEAGUE",

    "KOREA_K_LEAGUE",

    "CHINA_SUPER_LEAGUE",

    "AUSTRALIA_A_LEAGUE",

    "SAUDI_PRO_LEAGUE",

    "UEFA_CHAMPIONS_LEAGUE",

    "UEFA_EUROPA_LEAGUE",

    "FIFA_WORLD_CUP"

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

    ("Manchester United", "Tottenham"),

    ("Newcastle", "Brighton"),

    ("Real Madrid", "Barcelona"),

    ("Atletico Madrid", "Sevilla"),

    ("Valencia", "Villarreal"),

    ("AC Milan", "Inter"),

    ("Juventus", "Napoli"),

    ("Roma", "Lazio"),

    ("Bayern", "Dortmund"),

    ("Leipzig", "Leverkusen"),

    ("PSG", "Marseille"),

    ("Lyon", "Monaco"),

    ("Ajax", "PSV"),

    ("Benfica", "Porto"),

    ("Sporting", "Braga"),

    ("Galatasaray", "Fenerbahce"),

    ("Celtic", "Rangers"),

    ("Flamengo", "Palmeiras"),

    ("Boca Juniors", "River Plate"),

    ("Club America", "Tigres"),

    ("Al Hilal", "Al Nassr"),

    ("Ulsan Hyundai", "Jeonbuk"),

    ("Yokohama FM", "Kawasaki Frontale"),

    ("Shanghai Port", "Beijing Guoan"),

    ("Sydney FC", "Melbourne Victory"),

    ("LA Galaxy", "Inter Miami")

]


def generate_live_data():

    status = random.choice([

        "PRE",

        "PRE",

        "PRE",

        "H1",

        "H2",

        "HT"

    ])

    if status == "PRE":

        return {

            "liveStatus": "PRE",

            "minute": None,

            "injury": None

        }

    if status == "HT":

        return {

            "liveStatus": "HT",

            "minute": 45,

            "injury": 0

        }

    minute = random.randint(1, 45)

    injury = random.randint(0, 4)

    return {

        "liveStatus": status,

        "minute": minute,

        "injury": injury

    }


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

    liveData = generate_live_data()

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

        "liveStatus": liveData["liveStatus"],

        "minute": liveData["minute"],

        "injury": liveData["injury"],

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

        key=lambda x: x["timestamp"],

        reverse=True

    )

    return jsonify(data)


@app.route("/send_telegram", methods=["POST"])
def send_telegram():

    try:

        data = request.json

        message = data.get("message", "")

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

    )"

CHAT_ID = "YOUR_CHAT_ID"

SPORTS = [

    "ENGLISH_PREMIER_LEAGUE",

    "ENGLISH_CHAMPIONSHIP",

    "SPAIN_LA_LIGA",

    "ITALY_SERIE_A",

    "GERMANY_BUNDESLIGA",

    "FRANCE_LIGUE_ONE",

    "BELGIUM_FIRST_DIV",

    "PORTUGAL_PRIMEIRA_LIGA",

    "NETHERLANDS_EREDIVISIE",

    "TURKEY_SUPER_LIG",

    "SCOTLAND_PREMIERSHIP",

    "BRAZIL_SERIE_A",

    "ARGENTINA_PRIMERA",

    "USA_MLS",

    "JAPAN_J_LEAGUE",

    "KOREA_K_LEAGUE",

    "CHINA_SUPER_LEAGUE",

    "AUSTRALIA_A_LEAGUE",

    "SAUDI_PRO_LEAGUE",

    "UEFA_CHAMPIONS_LEAGUE",

    "UEFA_EUROPA_LEAGUE",

    "FIFA_WORLD_CUP"

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

    ("Manchester United", "Tottenham"),

    ("Newcastle", "Brighton"),

    ("Real Madrid", "Barcelona"),

    ("Atletico Madrid", "Sevilla"),

    ("Valencia", "Villarreal"),

    ("AC Milan", "Inter"),

    ("Juventus", "Napoli"),

    ("Roma", "Lazio"),

    ("Bayern", "Dortmund"),

    ("Leipzig", "Leverkusen"),

    ("PSG", "Marseille"),

    ("Lyon", "Monaco"),

    ("Ajax", "PSV"),

    ("Benfica", "Porto"),

    ("Sporting", "Braga"),

    ("Galatasaray", "Fenerbahce"),

    ("Celtic", "Rangers"),

    ("Flamengo", "Palmeiras"),

    ("Boca Juniors", "River Plate"),

    ("Club America", "Tigres"),

    ("Al Hilal", "Al Nassr"),

    ("Ulsan Hyundai", "Jeonbuk"),

    ("Yokohama FM", "Kawasaki Frontale"),

    ("Shanghai Port", "Beijing Guoan"),

    ("Sydney FC", "Melbourne Victory"),

    ("LA Galaxy", "Inter Miami")

]


def generate_live_data():

    status = random.choice([

        "PRE",

        "PRE",

        "PRE",

        "H1",

        "H2",

        "HT"

    ])

    if status == "PRE":

        return {

            "liveStatus": "PRE",

            "minute": None,

            "injury": None

        }

    if status == "HT":

        return {

            "liveStatus": "HT",

            "minute": 45,

            "injury": 0

        }

    minute = random.randint(1, 45)

    injury = random.randint(0, 4)

    return {

        "liveStatus": status,

        "minute": minute,

        "injury": injury

    }


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

    liveData = generate_live_data()

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

        "liveStatus": liveData["liveStatus"],

        "minute": liveData["minute"],

        "injury": liveData["injury"],

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

        key=lambda x: x["timestamp"],

        reverse=True

    )

    return jsonify(data)


@app.route("/send_telegram", methods=["POST"])
def send_telegram():

    try:

        data = request.json

        message = data.get("message", "")

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

    )"

CHAT_ID = "YOUR_CHAT_ID"

SPORTS = [

    "ENGLISH_PREMIER_LEAGUE",

    "ENGLISH_CHAMPIONSHIP",

    "SPAIN_LA_LIGA",

    "ITALY_SERIE_A",

    "GERMANY_BUNDESLIGA",

    "FRANCE_LIGUE_ONE",

    "BELGIUM_FIRST_DIV",

    "PORTUGAL_PRIMEIRA_LIGA",

    "NETHERLANDS_EREDIVISIE",

    "TURKEY_SUPER_LIG",

    "SCOTLAND_PREMIERSHIP",

    "BRAZIL_SERIE_A",

    "ARGENTINA_PRIMERA",

    "USA_MLS",

    "JAPAN_J_LEAGUE",

    "KOREA_K_LEAGUE",

    "CHINA_SUPER_LEAGUE",

    "AUSTRALIA_A_LEAGUE",

    "SAUDI_PRO_LEAGUE",

    "UEFA_CHAMPIONS_LEAGUE",

    "UEFA_EUROPA_LEAGUE",

    "FIFA_WORLD_CUP"

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

    ("Manchester United", "Tottenham"),

    ("Newcastle", "Brighton"),

    ("Real Madrid", "Barcelona"),

    ("Atletico Madrid", "Sevilla"),

    ("Valencia", "Villarreal"),

    ("AC Milan", "Inter"),

    ("Juventus", "Napoli"),

    ("Roma", "Lazio"),

    ("Bayern", "Dortmund"),

    ("Leipzig", "Leverkusen"),

    ("PSG", "Marseille"),

    ("Lyon", "Monaco"),

    ("Ajax", "PSV"),

    ("Benfica", "Porto"),

    ("Sporting", "Braga"),

    ("Galatasaray", "Fenerbahce"),

    ("Celtic", "Rangers"),

    ("Flamengo", "Palmeiras"),

    ("Boca Juniors", "River Plate"),

    ("Club America", "Tigres"),

    ("Al Hilal", "Al Nassr"),

    ("Ulsan Hyundai", "Jeonbuk"),

    ("Yokohama FM", "Kawasaki Frontale"),

    ("Shanghai Port", "Beijing Guoan"),

    ("Sydney FC", "Melbourne Victory"),

    ("LA Galaxy", "Inter Miami")

]


def generate_live_data():

    status = random.choice([

        "PRE",

        "PRE",

        "PRE",

        "H1",

        "H2",

        "HT"

    ])

    if status == "PRE":

        return {

            "liveStatus": "PRE",

            "minute": None,

            "injury": None

        }

    if status == "HT":

        return {

            "liveStatus": "HT",

            "minute": 45,

            "injury": 0

        }

    minute = random.randint(1, 45)

    injury = random.randint(0, 4)

    return {

        "liveStatus": status,

        "minute": minute,

        "injury": injury

    }


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

    liveData = generate_live_data()

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

        "liveStatus": liveData["liveStatus"],

        "minute": liveData["minute"],

        "injury": liveData["injury"],

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

        key=lambda x: x["timestamp"],

        reverse=True

    )

    return jsonify(data)


@app.route("/send_telegram", methods=["POST"])
def send_telegram():

    try:

        data = request.json

        message = data.get("message", "")

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