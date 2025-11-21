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
from texts import MESSAGES

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


class FinanceForm(StatesGroup):
    waiting_for_amount = State()
    waiting_for_comment = State()


# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

def get_role(user_id):
    if user_id in MANAGERS: return "manager"
    if user_id in EMPLOYEES: return "employee"
    return None


def get_category_code(text):
    """Ищет код категории по тексту кнопки."""
    for lang in MESSAGES:
        for key, value in MESSAGES[lang].items():
            if value == text:
                # Исключаем системные кнопки, оставляем только финансовые категории
                if key.startswith("btn_") and key not in ["btn_report", "btn_mgr_report", "btn_excel", "btn_reset",
                                                          "btn_cancel", "btn_help"]:
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


# --- ОБРАБОТКА КОМАНД ---

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


# --- ОБРАБОТКА КНОПКИ ПОМОЩЬ ---
# Срабатывает и на команду /help, и на нажатие кнопки

@dp.message(lambda msg: any(msg.text == MESSAGES[l]["btn_help"] for l in MESSAGES))
@dp.message(Command("help"))
async def cmd_help_handler(message: Message):
    user_id = message.from_user.id
    lang = await db.get_user_lang(user_id) or "ru"
    t = MESSAGES[lang]
    role = get_role(user_id)

    if role == "manager":
        text = t["help_text_manager"]
    elif role == "employee":
        text = t["help_text_employee"]
    else:
        text = t["access_denied"]

    await message.answer(text, parse_mode="HTML")


# --- ЛОГИКА ВВОДА ДАННЫХ (Sotrudnik) ---

@dp.message(lambda msg: get_category_code(msg.text) is not None)
async def start_input(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if get_role(user_id) != "employee": return

    lang = await db.get_user_lang(user_id) or "ru"
    cat_code = get_category_code(message.text)

    await state.update_data(category=cat_code, lang=lang)
    await state.set_state(FinanceForm.waiting_for_amount)
    await message.answer(MESSAGES[lang]["input_amount"], reply_markup=kb.get_cancel_kb(lang), parse_mode="HTML")


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
    t = MESSAGES[lang]

    try:
        # Убираем пробелы и меняем запятую на точку
        val = message.text.replace(',', '.').replace(' ', '')
        amount = float(val)

        await state.update_data(amount=amount)

        # Если это расход, просим комментарий
        if data['category'] == 'expense':
            await state.set_state(FinanceForm.waiting_for_comment)
            await message.answer(t["input_comment"], reply_markup=kb.get_cancel_kb(lang), parse_mode="HTML")
        else:
            await finish_transaction(message, state, "-")

    except ValueError:
        await message.answer(t["error_digit"], parse_mode="HTML")


@dp.message(FinanceForm.waiting_for_comment)
async def process_comment(message: Message, state: FSMContext):
    await finish_transaction(message, state, message.text)


async def finish_transaction(message: Message, state: FSMContext, comment: str):
    data = await state.get_data()
    lang = data['lang']
    user_id = message.from_user.id

    await db.add_transaction(user_id, EMPLOYEES[user_id], data['category'], data['amount'], comment)
    await state.clear()

    text = MESSAGES[lang]["saved"].format(amount=data['amount'], category=data['category'])
    await message.answer(text, reply_markup=kb.get_employee_kb(lang), parse_mode="HTML")


# --- ОТЧЕТЫ И УПРАВЛЕНИЕ ---

@dp.message(lambda msg: any(msg.text == MESSAGES[l]["btn_report"] for l in MESSAGES))
async def employee_report(message: Message):
    if get_role(message.from_user.id) != "employee": return

    lang = await db.get_user_lang(message.from_user.id) or "ru"
    location = EMPLOYEES[message.from_user.id]

    stats = await db.get_today_stats(location)
    revenue = stats['cash'] + stats['card'] + stats['qr']
    total = revenue - stats['refund'] - stats['expense']

    t = MESSAGES[lang]
    report = (
        f"{t['report_title'].format(location=location)}\n"
        f"🗓 {db.date.today()}\n\n"
        f"➕ <b>Выручка: {revenue:,.2f}</b>\n"
        f"  ├ 💵 {stats['cash']:,.2f}\n"
        f"  ├ 💳 {stats['card']:,.2f}\n"
        f"  └ 📱 {stats['qr']:,.2f}\n"
        f"➖➖➖➖➖\n"
        f"🧾 Чеков: {int(stats['checks'])}\n"
        f"🔙 Возвраты: {stats['refund']:,.2f}\n"
        f"📤 Расходы: {stats['expense']:,.2f}\n"
        f"➖➖➖➖➖\n"
        f"💰 <b>В КАССЕ: {total:,.2f}</b>"
    )
    await message.answer(report, parse_mode="HTML")


@dp.message(lambda msg: any(msg.text == MESSAGES[l]["btn_mgr_report"] for l in MESSAGES))
async def manager_report(message: Message):
    if get_role(message.from_user.id) != "manager": return

    lang = await db.get_user_lang(message.from_user.id) or "ru"
    stats = await db.get_today_stats()  # Общая статистика по всем точкам

    revenue = stats['cash'] + stats['card'] + stats['qr']
    total = revenue - stats['refund'] - stats['expense']

    text = (
        f"📊 <b>СВОДКА ПО ВСЕМ ТОЧКАМ</b>\n"
        f"🗓 {db.date.today()}\n\n"
        f"➕ Оборот: <b>{revenue:,.2f}</b>\n"
        f"➖ Расходы: <b>{stats['expense']:,.2f}</b>\n"
        f"🏁 Чистый итог: <b>{total:,.2f}</b>"
    )
    await message.answer(text, parse_mode="HTML")


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


@dp.message(lambda msg: any(msg.text == MESSAGES[l]["btn_reset"] for l in MESSAGES))
async def manager_reset(message: Message):
    if get_role(message.from_user.id) != "manager": return
    lang = await db.get_user_lang(message.from_user.id) or "ru"

    await db.reset_today()
    await message.answer(MESSAGES[lang]["reset_done"], parse_mode="HTML")


# --- ЗАПУСК ---
async def main():
    await db.init_db()
    print("Bot started successfully.")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped")
