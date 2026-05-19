import requests

BOT_TOKEN = "8925919932:AAE_CN7NRn9JCbtknc9RqwXdzc9xqfGpG6g"

CHAT_ID = "@sokeoscanner"

def send_telegram(message):

    url = (
        f"https://api.telegram.org/bot"
        f"{BOT_TOKEN}/sendMessage"
    )

    payload = {

        "chat_id": CHAT_ID,

        "text": message,

        "parse_mode": "HTML"

    }

    try:

        response = requests.post(
            url,
            data=payload
        )

        print(response.text)

    except Exception as e:

        print(e)

# TEST

send_telegram("""

🚨 VALUE MOVE ALERT

⚽ Monaco vs PSG

📉 Line: -2

SABA: 90
CMD: 95

📈 Diff: +5

""")