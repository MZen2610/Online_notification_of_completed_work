from dotenv import load_dotenv

import os
import requests
import telegram


def verified_works(token):
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
    text_bot = ""

    result_checking = verified_works(dvmn_token)
    if result_checking["new_attempts"][0]["is_negative"] == True:
        text = f'К сожалению, в работе нашлись ошибки.\n\n' \
                   f'ссылка на урок {result_checking["new_attempts"][0]["lesson_url"]}'
    else:
        text = "Преподавателю всё понравилось, можно приступать к следующему уроку."
    text_bot = f'У вас проверили работу "{result_checking["new_attempts"][0]["lesson_title"]}"\n\n {text}'


    bot = telegram.Bot(token=tgm_token)
    bot.send_message(chat_id=chat_id, text=text_bot)

if __name__ == '__main__':
    send_request()
