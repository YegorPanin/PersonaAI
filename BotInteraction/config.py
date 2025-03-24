import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "shared_resources"

# Настройки OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
AI_MODEL = "anthropic/claude-3-opus"

# Таймауты
DIALOG_TIMEOUT = 600  # 10 минут в секундах
POLL_INTERVAL = 0.1   # Интервал проверки очереди