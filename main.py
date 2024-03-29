from dotenv import load_dotenv

import os
import requests
import telegram
import time
import logging

logger = logging.getLogger("Logger")


class TelegramLogsHandler(logging.Handler):
    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


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
            logger.warning("Бот упал с ошибкой 'requests.exceptions.ReadTimeout'")
            continue
        except ConnectionError:
            logger.warning("Ошибка 'Connection Error'")
            time.sleep(600)


def main():
    load_dotenv()
    dvmn_token = os.environ["DVMN_TOKEN"]
    tgm_token = os.environ["TGM_TOKEN"]
    chat_id = os.environ["TGM_CHAT_ID"]

    logger.setLevel(logging.WARNING)
    logger.addHandler(TelegramLogsHandler(telegram.Bot(token=tgm_token), chat_id))
    logger.warning("Бот запущен")
    check_work(dvmn_token, tgm_token, chat_id)


if __name__ == "__main__":
    main()
