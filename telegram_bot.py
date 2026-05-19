import requests
import time

BOT_TOKEN = "8925919932:AAE_CN7NRn9JCbtknc9RqwXdzc9xqfGpG6g"

CHAT_ID = "@sokeoscanner"

API_URL = "https://oddssokeo-api-1.onrender.com/matches"

# =========================================
# SEND TELEGRAM
# =========================================

def send_telegram(message):

    url = (
        f"https://api.telegram.org/bot"
        f"{BOT_TOKEN}/sendMessage"
    )

    payload = {

        "chat_id": CHAT_ID,

        "text": message

    }

    response = requests.post(
        url,
        data=payload
    )

    print(response.text)

# =========================================
# LOOP
# =========================================

print("TELEGRAM BOT RUNNING")

sent_cache = set()

while True:

    try:

        response = requests.get(API_URL)

        matches = response.json()

        for item in matches:

            pi = float(item["pi"])

            key = (
                item["match"]
                + item["pi"]
            )

            if abs(pi) >= 0.05:

                if key not in sent_cache:

                    message = f"""
🚨 AH MOVEMENT ALERT

⚽ {item['match']}

📉 OPEN:
{item['open_ah']} @ {item['open_odds']}

📈 CURRENT:
{item['curr_ah']} @ {item['curr_odds']}

📊 PI: {item['pi']}
"""

                    send_telegram(message)

                    sent_cache.add(key)

        time.sleep(15)

    except Exception as e:

        print(e)

        time.sleep(10)