from dotenv import load_dotenv

import os
import requests
import telegram


def list_of_works(token):
    headers = {"Authorization": token}
    params = {}
    while True:
        try:
            response = requests.get("https://dvmn.org/api/long_polling",
                                    headers=headers,
                                    params=params,
                                    timeout=10
                                    )
            response.raise_for_status()
            if response.json()["status"] == "timeout":
                params = {"timestamp": response.json()["timestamp_to_request"]}
            return response.json()

        except requests.exceptions.ReadTimeout:
            continue
        except ConnectionError:
            continue


def send_request():
    load_dotenv()
    dvmn_token = os.environ["DVMN_TOKEN"]
    tgm_token = os.environ["TGM_TOKEN"]
    chat_id = os.environ["CHAT_ID"]

    text = list_of_works(dvmn_token)
    bot = telegram.Bot(token=tgm_token)
    bot.send_message(chat_id=chat_id, text=text)

if __name__ == '__main__':
    send_request()
