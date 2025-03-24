import os
import re
import random
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramAPIError, TelegramUnauthorizedError
from dotenv import load_dotenv
import aiosqlite

from bot.database import DatabaseHandler
from bot.openrouter import OpenRouterManager
from bot.keyboards import (
    create_main_keyboard,
    create_cancel_keyboard,
    create_confirmation_keyboard
)
from bot.states import BotCreationStates
from config import API_TOKEN, QUESTIONS_FILE

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



class TgBot:
    def __init__(self):
        print(API_TOKEN)
        self.bot = Bot(
            token=API_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        self.dp = Dispatcher(storage=MemoryStorage())
        self.router = Router()
        self.db = DatabaseHandler()
        self.ai = OpenRouterManager()
        self.questions = self.load_questions()
        self.random_phrases = [
            "🤖 Ой, я пока не понимаю такие команды! Попробуй 🆕 Создать бота",
            "✨ Кажется, я потерялся... Нажми кнопку 🆕 Создать бота",
            "🎈 Упс! Не распознал команду. Может /start?",
            "🔍 Не совсем понял. Нужна помощь? Нажми ❓ Помощь",
            "🌌 Вау, это что-то новенькое! Но я знаю только /newBot и /help",
            "🍩 Ммм, не уверен что это. Давай начнём с 🆕 Создать бота?",
            "🚀 Хочешь создать бота? Жми 🆕 Создать бота!",
            "🎭 Ой-ой, кажется, мы друг друга не поняли. Попробуй 🆕 Создать бота",
            "📚 Я пока учусь! Нажми 🆕 Создать бота",
            "🌈 Извини, я не понял. Давай начнём сначала с /start?"
        ]
        self.register_handlers()
        self.dp.include_router(self.router)

    def load_questions(self):
        """Загружает вопросы из файла, где каждый вопрос на новой строке"""
        try:
            with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
                # Читаем все строки, убираем пустые и строки только с пробелами
                questions = [line.strip() for line in f if line.strip()]
                logger.info(f"Загружено {len(questions)} вопросов")
                return questions
        except FileNotFoundError:
            logger.error(f"Файл {QUESTIONS_FILE} не найден")
            return []
        except Exception as e:
            logger.error(f"Ошибка при чтении файла: {e}")
            return []

    async def check_telegram_token(self, token: str) -> bool:
        try:
            temp_bot = Bot(token=token)
            await temp_bot.get_me()
            await temp_bot.session.close()
            return True
        except TelegramUnauthorizedError:
            return False
        except TelegramAPIError as e:
            logger.error(f"Telegram API error: {e}")
            return False
        except Exception as e:
            logger.error(f"Ошибка проверки токена: {e}")
            return False

    def register_handlers(self):
        @self.router.message(F.text == "❓ Помощь")
        async def start(message: types.Message):
            welcome_text = (
                """🤖 Привет! Я PersonaCrafter — твой инструмент для создания AI-ботов за минуты! 🚀
            
✨ Мои возможности:
— 🛠️ Шаг за шагом помогу разработать персонажа
— 🧠 Напишу яркое описание с помощью нейросети
— 🔒 Сохраню данные в защищённом хранилище

Как это работает?
1️⃣ Пришли свой токен (ключ для доступа)
2️⃣ Заполни простую анкету о персонаже
3️⃣ Получи готового бота!

Всё просто: два действия — и твой уникальный бот создан! 💡

Для начала - нажми кнопку 🆕 *Создать бота*
                    """)


            await message.answer(welcome_text,parse_mode=ParseMode.MARKDOWN,reply_markup=create_main_keyboard())

        @self.router.message(F.text == "🆕 Создать бота" or F.text == "/start")
        async def new_bot(message: types.Message, state: FSMContext):
            if await self.db.user_exists(message.from_user.id):
                await message.answer("🚨 У тебя уже есть бот! Хочешь создать нового? (скоро будет доступно) 😉",
                                     reply_markup=create_main_keyboard())
                return

            await state.set_state(BotCreationStates.waiting_token)
            await message.answer(
                """**🎯 Всё просто! 3 шага до твоего бота:**\n\n

1️⃣ **🔐 Получи секретный код**  
   — Открой @BotFather в Telegram  
   — Нажми /newbot → придумай имя боту → скопируй строку **«API Token»**  

2️⃣ **📩 Отправь его сюда**  
   — Вставь код в сообщение *точно как есть* (пример: `12345:AbcDefGhIJKLmNoPQRsTuV`)  
   — 🔒 *Это как ключ от замка — никому не показывай!*  

3️⃣ **✨ Наслаждайся!**  
   — Я сам настрою персонажа по твоим правилам  
   — Останется только запустить бота 🚀 
                   """,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=create_cancel_keyboard()
            )

        @self.router.message(F.text == "❌ Отмена")
        async def cancel_handler(message: types.Message, state: FSMContext):
            await state.clear()
            await message.answer("❌ Действие отменено", reply_markup=create_main_keyboard())

        @self.router.message(BotCreationStates.waiting_token)
        async def process_token(message: types.Message, state: FSMContext):
            token = message.text.strip()

            if not re.match(r'^\d+:[a-zA-Z0-9_-]+$', token):
                await message.answer("❌ Неверный формат токена! Пример: 1234567890:ABCdefGHIJKLMNopqrstUVWXYZ")
                return

            await message.answer("🔍 Проверяю токен...")

            if not await self.check_telegram_token(token):
                await message.answer("🚨 Токен недействителен! Проверь его и попробуй снова")
                return

            try:
                temp_bot = Bot(token=token)
                bot_info = await temp_bot.get_me()
                await temp_bot.session.close()

                await self.db.add_user(message.from_user.id, token)
                await message.answer(
                    f"✅ Токен действителен! Привет, {bot_info.full_name} (@{bot_info.username})!\n\n"
                    "Теперь создадим описание! 🎨 Отвечай на вопросы, а я сгенерирую крутое описание! ✨",
                    reply_markup=types.ReplyKeyboardRemove()
                )

                await state.set_state(BotCreationStates.interview)
                await state.update_data(current_question=0, answers=[])
                await self.ask_question(message, state)

            except aiosqlite.IntegrityError:
                await message.answer("🚨 Этот токен уже занят! Придумай другой")
            except Exception as e:
                logger.error(f"Ошибка при обработке токена: {e}")
                await message.answer("😢 Упс! Что-то пошло не так. Попробуй позже")

        @self.router.message(BotCreationStates.interview)
        async def process_answer(message: types.Message, state: FSMContext):
            data = await state.get_data()
            current = data['current_question']

            if current >= len(self.questions):
                await self.finish_interview(message, state)
                return

            answers = data.get('answers', [])
            answers.append((self.questions[current], message.text))
            await state.update_data(answers=answers, current_question=current + 1)
            await self.ask_question(message, state)

        @self.router.callback_query(BotCreationStates.confirmation)
        async def confirm_description(callback: types.CallbackQuery, state: FSMContext):
            if callback.data == "confirm_yes":
                data = await state.get_data()
                await self.db.update_description(callback.from_user.id, data['description'])
                await callback.message.edit_reply_markup()
                await callback.message.answer(
                    "✅ *Описание сохранено!* Теперь можешь установить аватар через @BotFather 🎉\n"
                    "Скоро добавлю новые функции! Следи за обновлениями 😉",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=create_main_keyboard()
                )
            else:
                await callback.message.edit_reply_markup()
                await callback.message.answer("🔄 Хорошо! Начнём заново? Жми 🆕 Создать бота",
                                              reply_markup=create_main_keyboard())
            await state.clear()

        @self.router.message()
        async def unknown_message(message: types.Message):
            if message.text.startswith('/') and not message.text == ("/start"):
                await message.answer("⚠️ Используй кнопки для навигации!", reply_markup=create_main_keyboard())
            else:
                await message.answer(random.choice(self.random_phrases), reply_markup=create_main_keyboard())

    async def ask_question(self, message: types.Message, state: FSMContext):
        data = await state.get_data()
        current = data['current_question']

        if current >= len(self.questions):
            await self.finish_interview(message, state)
            return

        question = f"❓ *Вопрос {current + 1}/{len(self.questions)}:*\n{self.questions[current]}"
        await message.answer(question, parse_mode=ParseMode.MARKDOWN)

    async def finish_interview(self, message: types.Message, state: FSMContext):
        data = await state.get_data()
        try:
            await message.answer("🧠 Начинаю генерацию описания... Это займет пару секунд ⏳")
            description = await self.ai.generate_description(data['answers'])
            await state.update_data(description=description)
            await state.set_state(BotCreationStates.confirmation)

            response_text = f"🎉 *Вот что у меня получилось!*\n\n{description}\n\nВсё верно?"
            await message.answer(response_text,
                                 parse_mode=ParseMode.MARKDOWN,
                                 reply_markup=create_confirmation_keyboard())

        except Exception as e:
            logger.error(f"OpenRouter error: {e}")
            await message.answer("😢 Упс! Что-то пошло не так. Попробуй позже",
                                 reply_markup=create_main_keyboard())
            await state.clear()

    async def run(self):
        await self.db.create_tables()
        await self.dp.start_polling(self.bot)


if __name__ == '__main__':
    bot = TgBot()
    asyncio.run(bot.run())