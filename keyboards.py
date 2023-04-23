from aiogram.types import (
                        KeyboardButton,
                        ReplyKeyboardMarkup,
                        InlineKeyboardMarkup,
                        InlineKeyboardButton,
                    )


keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

buttons = [
    'Температура на улице',
    'Конвертировать валюту',
    'Получить котика 🐈',
    'Показать мой IP',
]

keyboard.add(*buttons)
