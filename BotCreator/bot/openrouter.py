from aiohttp import ClientSession
from config import OPENROUTER_URL, AI_MODEL, OPENROUTER_API_KEY
import logging
import asyncio

logger = logging.getLogger(__name__)


class OpenRouterManager:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/myrepo",  # Добавьте ваш URL
            "X-Title": "PersonaCrafter"  # Добавьте название вашего приложения
        }

    async def generate_description(self, answers: list) -> str:
        if not answers:
            raise ValueError("Список ответов не может быть пустым")

        # Если передана строка вместо списка (для тестирования)
        if isinstance(answers, str):
            answers = [("Характер персонажа", answers)]

        prompt = "Создай подробное описание персонажа на основе этих ответов:\n"
        prompt += "\n".join(f"Вопрос: {q}\nОтвет: {a}" for q, a in answers)

        try:
            async with ClientSession() as session:
                async with session.post(
                        OPENROUTER_URL,
                        headers=self.headers,
                        json={
                            "model": AI_MODEL,
                            "messages": [{"role": "user", "content": prompt}]
                        }
                ) as response:
                    response.raise_for_status()  # Проверяем статус ответа
                    response_data = await response.json()
                    return response_data['choices'][0]['message']['content']

        except Exception as e:
            logger.error(f"OpenRouter error: {e}")
            raise
