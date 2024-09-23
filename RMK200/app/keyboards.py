from aiogram.types import KeyboardButton,ReplyKeyboardMarkup
button=[
    [KeyboardButton(text="курсы криптовалют "),KeyboardButton(text="/help ") ]
]

keyboard1 = ReplyKeyboardMarkup(keyboard=button, resize_keyboard=True)