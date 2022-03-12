from dotenv import load_dotenv

import os
import requests
import telegram
import time


def send_telegram_message(checking_result, tgm_token, chat_id):
    text = ""
    lesson_title = ""
    for key_result, value_result in checking_result.items():
        if key_result == "new_attempts":
            for values_new_attempt in value_result:
                for key_new_attempt, value_new_attempt in values_new_attempt.items():
                    if key_new_attempt == "is_negative" and value_new_attempt:
                        text = f'К сожалению, в работе нашлись ошибки.\n\n'
                    elif key_new_attempt == "is_negative" and not value_new_attempt:
                        text = "Преподавателю всё понравилось, можно приступать к следующему уроку."
                    elif key_new_attempt == "lesson_url":
                        text += f'ссылка на урок {value_new_attempt}'
                    elif key_new_attempt == "lesson_title":
                        lesson_title = value_new_attempt

    text_bot = f'У вас проверили работу "{lesson_title}"\n\n {text}'

    bot = telegram.Bot(token=tgm_token)
    bot.send_message(chat_id=chat_id, text=text_bot)


def get_verified_works(dvmn_token, tgm_token, chat_id):
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
    get_verified_works(dvmn_token, tgm_token, chat_id)


if __name__ == '__main__':
    main()
