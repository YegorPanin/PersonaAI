import time
from datetime import datetime
from .database.crud import get_bot_description, save_story
from .config import AI_MODEL, OPENROUTER_URL, OPENROUTER_API_KEY
import requests


def run_dialog_process(user_id: int, bot_id: int, queue: Queue):
    bot_description = get_bot_description(bot_id)
    last_active = datetime.now()

    while True:
        # Проверка таймаута
        if (datetime.now() - last_active).total_seconds() > config.DIALOG_TIMEOUT:
            break

        # Обработка сообщений
        if not queue.empty():
            message = queue.get()
            last_active = datetime.now()

            # Генерация ответа
            response = generate_response(bot_description, message)

            # Сохранение истории
            save_story(user_id, bot_id, message, response)

        time.sleep(config.POLL_INTERVAL)


def generate_response(description: str, message: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": AI_MODEL,
        "messages": [
            {"role": "system", "content": description},
            {"role": "user", "content": message}
        ]
    }

    response = requests.post(OPENROUTER_URL, json=data, headers=headers)
    return response.json()['choices'][0]['message']['content']