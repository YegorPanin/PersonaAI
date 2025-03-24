from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def create_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🆕 Создать бота")],
            [KeyboardButton(text="❓ Помощь"), KeyboardButton(text="📄 Мой бот")]
        ],
        resize_keyboard=True
    )

def create_cancel_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True
    )

def create_confirmation_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Всё верно", callback_data="confirm_yes"),
                InlineKeyboardButton(text="🔄 Переделать", callback_data="confirm_no")
            ]
        ]
    )