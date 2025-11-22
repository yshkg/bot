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
        [KeyboardButton(text=t["btn_cash"]), KeyboardButton(text=t["btn_card"]), KeyboardButton(text=t["btn_qr"])],
        [KeyboardButton(text=t["btn_expense"]), KeyboardButton(text=t["btn_checks"]), KeyboardButton(text=t["btn_refund"])],
        # Нижний ряд: Отчет | Язык | Помощь
        [KeyboardButton(text=t["btn_report"]), KeyboardButton(text=t["btn_lang"]), KeyboardButton(text=t["btn_help"])]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_manager_kb(lang="ru"):
    t = MESSAGES[lang]
    kb = [
        [KeyboardButton(text=t["btn_mgr_report"]), KeyboardButton(text=t["btn_analytics"])],
        [KeyboardButton(text=t["btn_excel"]), KeyboardButton(text=t["btn_ai"])],
        # Нижний ряд: Сброс | Язык | Помощь
        [KeyboardButton(text=t["btn_reset"]), KeyboardButton(text=t["btn_lang"]), KeyboardButton(text=t["btn_help"])]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_expense_kb(lang="ru"):
    t = MESSAGES[lang]
    kb = [
        [KeyboardButton(text=t["exp_products"]), KeyboardButton(text=t["exp_supplies"])],
        [KeyboardButton(text=t["exp_salary"]), KeyboardButton(text=t["exp_rent"])],
        [KeyboardButton(text=t["exp_other"]), KeyboardButton(text=t["btn_cancel"])]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_cancel_kb(lang="ru"):
    t = MESSAGES[lang]
    kb = [[KeyboardButton(text=t["btn_cancel"])]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
