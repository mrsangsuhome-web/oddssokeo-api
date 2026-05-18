import requests

BOT_TOKEN = "8925919932:AAE_CN7NRn9JCbtknc9RqwXdzc9xqfGpG6g"

CHAT_ID = "@sokeoscanner_bot"

def send_telegram(message):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {

        "chat_id": CHAT_ID,

        "text": message

    }

    try:

        requests.post(url, data=payload)

        print("Telegram sent")

    except Exception as e:

        print(e)

# TEST ALERTS

send_telegram("⚡ Có trận mới được cập nhật")

send_telegram("🔥 Live scanner đang hoạt động")

send_telegram("📈 Odds movement detected")

send_telegram("🟢 API online")