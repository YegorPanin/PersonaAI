
from pathlib import Path

BASE_DIR = Path(__file__).parent

# Настройки
API_TOKEN = "7824413362:AAFCX8do9QucewviXq66u0S7sH9EvZ8A7rg"
OPENROUTER_API_KEY = "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"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
QUESTIONS_FILE = BASE_DIR / "questions.txt"
DATABASE_NAME = BASE_DIR / "bots.db"
AI_MODEL = "meta-llama/llama-3.2-3b-instruct:free"