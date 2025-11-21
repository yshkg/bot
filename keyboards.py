from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from texts import MESSAGES

def get_lang_kb():
    kb = [
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_employee_kb(lang="ru"):
    t = MESSAGES[lang]
    kb = [
        [KeyboardButton(text=t["btn_cash"]), KeyboardButton(text=t["btn_card"])],
        [KeyboardButton(text=t["btn_qr"]), KeyboardButton(text=t["btn_checks"])],
        [KeyboardButton(text=t["btn_refund"]), KeyboardButton(text=t["btn_expense"])],
        [KeyboardButton(text=t["btn_report"]), KeyboardButton(text=t["btn_help"])]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_manager_kb(lang="ru"):
    t = MESSAGES[lang]
    kb = [
        [KeyboardButton(text=t["btn_mgr_report"])],
        # Кнопка AI и Excel в одном ряду
        [KeyboardButton(text=t["btn_ai"]), KeyboardButton(text=t["btn_excel"])],
        [KeyboardButton(text=t["btn_reset"]), KeyboardButton(text=t["btn_help"])]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_cancel_kb(lang="ru"):
    t = MESSAGES[lang]
    kb = [[KeyboardButton(text=t["btn_cancel"])]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
