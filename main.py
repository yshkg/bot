import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import BOT_TOKEN, MANAGERS, EMPLOYEES
import database as db
import keyboards as kb
import ai_service  # <-- Подключаем наш AI модуль
from texts import MESSAGES

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


class FinanceForm(StatesGroup):
    waiting_for_amount = State()
    waiting_for_comment = State()


# --- Утилиты ---
def get_role(user_id):
    if user_id in MANAGERS: return "manager"
    if user_id in EMPLOYEES: return "employee"
    return None


def get_category_code(text):
    for lang in MESSAGES:
        for key, value in MESSAGES[lang].items():
            if value == text:
                if key.startswith("btn_") and key not in ["btn_report", "btn_mgr_report", "btn_excel", "btn_reset",
                                                          "btn_cancel", "btn_help", "btn_ai"]:
                    return key.replace("btn_", "")
    return None


async def show_main_menu(message: Message, user_id, lang):
    role = get_role(user_id)
    t = MESSAGES[lang]
    if role == "manager":
        await message.answer(t["welcome_manager"], reply_markup=kb.get_manager_kb(lang), parse_mode="HTML")
    elif role == "employee":
        point = EMPLOYEES[user_id]
        await message.answer(t["welcome_employee"].format(point=point), reply_markup=kb.get_employee_kb(lang),
                             parse_mode="HTML")
    else:
        await message.answer(t["access_denied"], parse_mode="HTML")


# --- Start / Lang ---
@dp.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    lang = await db.get_user_lang(user_id)
    if not lang:
        await message.answer(MESSAGES["ru"]["choose_lang"], reply_markup=kb.get_lang_kb())
    else:
        await show_main_menu(message, user_id, lang)


@dp.message(Command("lang"))
async def cmd_lang(message: Message):
    await message.answer(MESSAGES["ru"]["choose_lang"], reply_markup=kb.get_lang_kb())


@dp.callback_query(F.data.startswith("lang_"))
async def lang_selection(callback: CallbackQuery):
    lang_code = callback.data.split("_")[1]
    user_id = callback.from_user.id
    await db.set_user_lang(user_id, lang_code)
    await callback.message.delete()
    await callback.message.answer(MESSAGES[lang_code]["lang_changed"])
    await show_main_menu(callback.message, user_id, lang_code)


@dp.message(lambda msg: any(msg.text == MESSAGES[l]["btn_help"] for l in MESSAGES))
@dp.message(Command("help"))
async def cmd_help(message: Message):
    user_id = message.from_user.id
    lang = await db.get_user_lang(user_id) or "ru"
    t = MESSAGES[lang]
    role = get_role(user_id)
    text = t["help_text_manager"] if role == "manager" else t["help_text_employee"] if role == "employee" else t[
        "access_denied"]
    await message.answer(text, parse_mode="HTML")


# --- Ввод данных ---
@dp.message(lambda msg: get_category_code(msg.text) is not None)
async def start_input(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if get_role(user_id) != "employee": return
    lang = await db.get_user_lang(user_id) or "ru"
    cat_code = get_category_code(message.text)
    await state.update_data(category=cat_code, lang=lang)
    await state.set_state(FinanceForm.waiting_for_amount)
    await message.answer(MESSAGES[lang]["input_amount"], reply_markup=kb.get_cancel_kb(lang))


@dp.message(lambda msg: any(msg.text == MESSAGES[l]["btn_cancel"] for l in MESSAGES), StateFilter("*"))
async def cancel_action(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await db.get_user_lang(user_id) or "ru"
    await state.clear()
    await message.answer(MESSAGES[lang]["cancelled"], reply_markup=kb.get_employee_kb(lang))


@dp.message(FinanceForm.waiting_for_amount)
async def process_amount(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data['lang']
    try:
        amount = float(message.text.replace(',', '.').replace(' ', ''))
        await state.update_data(amount=amount)
        if data['category'] == 'expense':
            await state.set_state(FinanceForm.waiting_for_comment)
            await message.answer(MESSAGES[lang]["input_comment"], reply_markup=kb.get_cancel_kb(lang))
        else:
            await finish_transaction(message, state, "-")
    except ValueError:
        await message.answer(MESSAGES[lang]["error_digit"])


@dp.message(FinanceForm.waiting_for_comment)
async def process_comment(message: Message, state: FSMContext):
    await finish_transaction(message, state, message.text)


async def finish_transaction(message: Message, state: FSMContext, comment: str):
    data = await state.get_data()
    lang = data['lang']
    user_id = message.from_user.id
    await db.add_transaction(user_id, EMPLOYEES[user_id], data['category'], data['amount'], comment)
    await state.clear()
    await message.answer(MESSAGES[lang]["saved"].format(amount=data['amount'], category=data['category']),
                         reply_markup=kb.get_employee_kb(lang))


# --- Отчеты и AI ---

@dp.message(lambda msg: any(msg.text == MESSAGES[l]["btn_report"] for l in MESSAGES))
async def employee_report(message: Message):
    if get_role(message.from_user.id) != "employee": return
    lang = await db.get_user_lang(message.from_user.id) or "ru"
    location = EMPLOYEES[message.from_user.id]
    stats = await db.get_today_stats(location)
    revenue = stats['cash'] + stats['card'] + stats['qr']
    total = revenue - stats['refund'] - stats['expense']
    await message.answer(f"📊 {location}\n+{revenue}\n-{stats['expense']}\n= {total}")


@dp.message(lambda msg: any(msg.text == MESSAGES[l]["btn_mgr_report"] for l in MESSAGES))
async def manager_report(message: Message):
    if get_role(message.from_user.id) != "manager": return
    stats = await db.get_today_stats()
    revenue = stats['cash'] + stats['card'] + stats['qr']
    total = revenue - stats['refund'] - stats['expense']
    await message.answer(f"📊 ALL POINTS\nRevenue: {revenue}\nTotal: {total}")


@dp.message(lambda msg: any(msg.text == MESSAGES[l]["btn_excel"] for l in MESSAGES))
async def manager_excel(message: Message):
    if get_role(message.from_user.id) != "manager": return
    lang = await db.get_user_lang(message.from_user.id) or "ru"
    await message.answer(MESSAGES[lang]["report_generated"])
    path = await db.export_to_excel()
    if path:
        await message.answer_document(FSInputFile(path))
        os.remove(path)
    else:
        await message.answer(MESSAGES[lang]["no_data"])


# --- ОБРАБОТЧИК AI АНАЛИЗА ---
@dp.message(lambda msg: any(msg.text == MESSAGES[l]["btn_ai"] for l in MESSAGES))
async def manager_ai_analysis(message: Message):
    if get_role(message.from_user.id) != "manager": return

    lang = await db.get_user_lang(message.from_user.id) or "ru"
    # Сообщение "Думаю..."
    await message.answer(MESSAGES[lang]["ai_thinking"], parse_mode="HTML")

    # 1. Получаем данные из БД
    report_text = await db.get_weekly_summary()

    # 2. Отправляем Гуглу
    ai_response = await ai_service.analyze_data(report_text)

    # 3. Отвечаем пользователю (БЕЗОПАСНЫЙ РЕЖИМ)
    try:
        # Сначала пробуем отправить красиво (Markdown)
        await message.answer(ai_response, parse_mode="Markdown")
    except Exception:
        # Если Телеграм ругается на спецсимволы — отправляем как обычный чистый текст
        # Это предотвращает ошибку "Bad Request: can't parse entities"
        await message.answer(ai_response)


@dp.message(lambda msg: any(msg.text == MESSAGES[l]["btn_reset"] for l in MESSAGES))
async def manager_reset(message: Message):
    if get_role(message.from_user.id) != "manager": return
    lang = await db.get_user_lang(message.from_user.id) or "ru"
    await db.reset_today()
    await message.answer(MESSAGES[lang]["reset_done"])


async def main():
    await db.init_db()
    print("Bot started + Gemini AI...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped")
