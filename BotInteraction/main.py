from aiogram import Bot, Dispatcher, types
from process_manager import DialogManager
import asyncio
import config

bot = Bot(token="YOUR_TELEGRAM_TOKEN")
dp = Dispatcher()
manager = DialogManager()


async def message_handler(message: types.Message):
    user_id = message.from_user.id
    bot_id = detect_bot_id(message.text)  # Ваша логика определения бота

    manager.start_dialog(user_id, bot_id)
    manager.send_message(user_id, bot_id, message.text)

    # Запуск периодической очистки
    asyncio.create_task(periodic_cleanup())


async def periodic_cleanup():
    while True:
        manager.cleanup()
        await asyncio.sleep(60)  # Проверка каждую минуту


if __name__ == '__main__':
    from aiogram import executor

    dp.register_message_handler(message_handler)
    executor.start_polling(dp, skip_updates=True)