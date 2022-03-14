from dotenv import load_dotenv

import os
import requests
import telegram
import time
import logging


def send_telegram_message(checking_result, tgm_token, chat_id):
    last_attempt = checking_result['new_attempts'][0]
    if last_attempt["is_negative"]:
        text = f'К сожалению, в работе нашлись ошибки.\n\n' \
               f'ссылка на урок {last_attempt["lesson_url"]}'
    else:
        text = "Преподавателю всё понравилось, можно приступать к следующему уроку."

    text_bot = f'У вас проверили работу "{last_attempt["lesson_title"]}"\n\n {text}'

    bot = telegram.Bot(token=tgm_token)
    bot.send_message(chat_id=chat_id, text=text_bot)


def check_work(dvmn_token, tgm_token, chat_id):
    headers = {"Authorization": dvmn_token}
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
            elif result["status"] == "found":
                send_telegram_message(result, tgm_token, chat_id)
        except requests.exceptions.ReadTimeout:
            continue
        except ConnectionError:
            time.sleep(600)


def main():
    load_dotenv()
    dvmn_token = os.environ["DVMN_TOKEN"]
    tgm_token = os.environ["TGM_TOKEN"]
    chat_id = os.environ["TGM_CHAT_ID"]
    logging.warning("Бот запущен")
    check_work(dvmn_token, tgm_token, chat_id)


if __name__ == '__main__':
    main()
