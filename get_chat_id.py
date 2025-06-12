import requests

BOT_TOKEN = '7565937945:AAGEoHuAhoiNU-MAEXHQc6bF_8lr14_LgzA'

def get_updates():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    response = requests.get(url)
    data = response.json()

    for update in data["result"]:
        try:
            chat_id = update["message"]["chat"]["id"]
            user_name = update["message"]["chat"].get("username", "N/A")
            print(f"Chat ID: {chat_id} from @{user_name}")
        except KeyError:
            continue

get_updates()
