import multiprocessing
import logging
from datetime import datetime
from multiprocessing import Process, Queue, Manager
from typing import Dict, Tuple, Any
import time
from dialog_process import *

# Настройка логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ProcessManager")


class DialogManager:
    def __init__(self, timeout: int = 600):
        self.manager = Manager()
        self.active_dialogs: Dict[Tuple[int, int], Dict[str, Any]] = self.manager.dict()
        self.lock = self.manager.Lock()
        self.timeout = timeout
        self._running = True

        # Запуск фоновой задачи для очистки
        self.cleanup_process = Process(target=self._cleanup_worker)
        self.cleanup_process.start()

    def _cleanup_worker(self):
        """Фоновый процесс для периодической очистки"""
        while self._running:
            time.sleep(60)  # Проверка каждую минуту
            self.cleanup()
            logger.debug("Выполнена фоновая очистка")

    def start_dialog(self, user_id: int, bot_id: int) -> bool:
        """Запуск нового диалога"""
        try:
            with self.lock:
                key = (user_id, bot_id)

                if key not in self.active_dialogs:
                    queue = self.manager.Queue()
                    process = Process(
                        target=run_dialog_process,
                        args=(user_id, bot_id, queue, self.timeout)

                    self.active_dialogs[key] = {
                        'process': process,
                        'queue': queue,
                        'last_active': datetime.now().timestamp()
                    }

                    process.start()
                    logger.info(f"Запущен новый диалог для {key}")
                    return True
                return False

        except Exception as e:
            logger.error(f"Ошибка запуска диалога: {e}")
            return False

    def send_message(self, user_id: int, bot_id: int, message: str) -> bool:
        """Отправка сообщения в диалог"""
        try:
            key = (user_id, bot_id)

            with self.lock:
                if key not in self.active_dialogs:
                    logger.warning(f"Диалог {key} не найден")
                    return False

                dialog = self.active_dialogs[key]
                dialog['queue'].put(message)
                dialog['last_active'] = datetime.now().timestamp()
                logger.debug(f"Сообщение отправлено в {key}")
                return True

        except Exception as e:
            logger.error(f"Ошибка отправки сообщения: {e}")
            return False

    def _terminate_dialog(self, key: Tuple[int, int]):
        """Корректное завершение диалога"""
        try:
            dialog = self.active_dialogs.get(key)
            if not dialog:
                return

            process = dialog['process']
            queue = dialog['queue']

            if process.is_alive():
                process.terminate()
                process.join(timeout=5)

            queue.close()
            del self.active_dialogs[key]
            logger.info(f"Диалог {key} завершен")

        except Exception as e:
            logger.error(f"Ошибка завершения диалога {key}: {e}")

    def cleanup(self):
        """Очистка неактивных диалогов"""
        try:
            current_time = datetime.now().timestamp()
            to_remove = []

            with self.lock:
                for key, dialog in self.active_dialogs.items():
                    last_active = dialog['last_active']
                    if (current_time - last_active) > self.timeout:
                        to_remove.append(key)

            for key in to_remove:
                self._terminate_dialog(key)

        except Exception as e:
            logger.error(f"Ошибка очистки: {e}")

    def shutdown(self):
        """Корректное завершение всех процессов"""
        self._running = False
        self.cleanup_process.terminate()

        with self.lock:
            for key in list(self.active_dialogs.keys()):
                self._terminate_dialog(key)

        self.manager.shutdown()
        logger.info("Менеджер процессов остановлен")


if __name__ == "__main__":
    # Пример использования
    manager = DialogManager(timeout=300)

    # Запуск тестового диалога
    manager.start_dialog(user_id=1, bot_id=100)
    manager.send_message(1, 100, "Привет!")

    # Дать время на выполнение
    time.sleep(2)

    # Корректное завершение
    manager.shutdown()