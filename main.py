from dotenv import load_dotenv

import os
import requests
import telegram
import time

load_dotenv()
dvmn_token = os.environ["DVMN_TOKEN"]
tgm_token = os.environ["TGM_TOKEN"]
chat_id = os.environ["TGM_CHAT_ID"]


def send_telegram_message(checking_result):
    if checking_result["new_attempts"][0]["is_negative"] == True:
        text = f'К сожалению, в работе нашлись ошибки.\n\n' \
               f'ссылка на урок {checking_result["new_attempts"][0]["lesson_url"]}'
    else:
        text = "Преподавателю всё понравилось, можно приступать к следующему уроку."
    text_bot = f'У вас проверили работу "{checking_result["new_attempts"][0]["lesson_title"]}"\n\n {text}'

    bot = telegram.Bot(token=tgm_token)
    bot.send_message(chat_id=chat_id, text=text_bot)


def get_verified_works(token):
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
            result = response.json()
            if result["status"] == "timeout":
                params = {"timestamp": result["timestamp_to_request"]}
            send_telegram_message(result)
        except requests.exceptions.ReadTimeout:
            continue
        except ConnectionError:
            time.sleep(600)


def main():
    get_verified_works(dvmn_token)


if __name__ == '__main__':
    main()
