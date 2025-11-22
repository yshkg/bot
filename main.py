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
import ai_service
from texts import MESSAGES, DAYS_RU, DAYS_EN

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


class FinanceForm(StatesGroup):
    waiting_for_expense_category = State()
    waiting_for_amount = State()
    waiting_for_comment = State()


# --- УТИЛИТЫ ---
def get_role(user_id):
    if user_id in MANAGERS: return "manager"
    if user_id in EMPLOYEES: return "employee"
    return None


def get_btn_key(text, lang):
    for key, val in MESSAGES[lang].items():
        if val == text: return key
    return None


async def show_menu(message: Message, user_id, lang):
    role = get_role(user_id)
    if role == "manager":
        await message.answer(MESSAGES[lang]["welcome_manager"], reply_markup=kb.get_manager_kb(lang), parse_mode="HTML")
    elif role == "employee":
        point = EMPLOYEES[user_id]
        await message.answer(MESSAGES[lang]["welcome_employee"].format(point=point),
                             reply_markup=kb.get_employee_kb(lang), parse_mode="HTML")


# --- START / LANG / HELP (ТУТ ОБНОВЛЕНИЯ) ---

@dp.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    lang = await db.get_user_lang(user_id)
    if not lang:
        await message.answer(MESSAGES["ru"]["choose_lang"], reply_markup=kb.get_lang_kb())
    else:
        await show_menu(message, user_id, lang)


@dp.message(lambda msg: any(msg.text == MESSAGES[l]["btn_lang"] for l in MESSAGES))
@dp.message(Command("lang"))
async def cmd_lang(message: Message):
    await message.answer(MESSAGES["ru"]["choose_lang"], reply_markup=kb.get_lang_kb())


@dp.callback_query(F.data.startswith("lang_"))
async def lang_selection(callback: CallbackQuery):
    lang = callback.data.split("_")[1]
    await db.set_user_lang(callback.from_user.id, lang)
    await callback.message.delete()
    await callback.message.answer(MESSAGES[lang]["lang_changed"])
    await show_menu(callback.message, callback.from_user.id, lang)


# 🔥 ОБРАБОТЧИК КНОПКИ HELP
@dp.message(lambda msg: any(msg.text == MESSAGES[l]["btn_help"] for l in MESSAGES))
@dp.message(Command("help"))
async def cmd_help(message: Message):
    user_id = message.from_user.id
    lang = await db.get_user_lang(user_id) or "ru"
    role = get_role(user_id)
    t = MESSAGES[lang]

    # Заголовок
    text = t["help_header"]

    # Инструкция в зависимости от роли
    if role == "manager":
        text += t["help_manager"]
    elif role == "employee":
        text += t["help_employee"]
    else:
        text += t["access_denied"]

    await message.answer(text, parse_mode="HTML")


# --- ЛОГИКА ВВОДА ---

@dp.message(lambda msg: get_btn_key(msg.text, "ru") in ["btn_cash", "btn_card", "btn_qr", "btn_checks",
                                                        "btn_refund"] or get_btn_key(msg.text, "en") in ["btn_cash",
                                                                                                         "btn_card",
                                                                                                         "btn_qr",
                                                                                                         "btn_checks",
                                                                                                         "btn_refund"])
async def start_simple_input(message: Message, state: FSMContext):
    if get_role(message.from_user.id) != "employee": return
    lang = await db.get_user_lang(message.from_user.id)
    key = get_btn_key(message.text, lang)
    category = key.replace("btn_", "")
    await state.update_data(category=category, lang=lang)
    await state.set_state(FinanceForm.waiting_for_amount)
    await message.answer(MESSAGES[lang]["enter_amount"], reply_markup=kb.get_cancel_kb(lang), parse_mode="HTML")


@dp.message(lambda msg: any(msg.text == MESSAGES[l]["btn_expense"] for l in MESSAGES))
async def start_expense(message: Message, state: FSMContext):
    if get_role(message.from_user.id) != "employee": return
    lang = await db.get_user_lang(message.from_user.id)
    await state.update_data(lang=lang)
    await message.answer(MESSAGES[lang]["choose_category"], reply_markup=kb.get_expense_kb(lang))
    await state.set_state(FinanceForm.waiting_for_expense_category)


@dp.message(FinanceForm.waiting_for_expense_category)
async def process_expense_cat(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data['lang']
    if message.text == MESSAGES[lang]["btn_cancel"]:
        await state.clear()
        await show_menu(message, message.from_user.id, lang)
        return
    key = get_btn_key(message.text, lang)
    if not key or not key.startswith("exp_"):
        await message.answer(MESSAGES[lang]["choose_category"])
        return
    await state.update_data(category=key)
    await state.set_state(FinanceForm.waiting_for_amount)
    await message.answer(MESSAGES[lang]["enter_amount"], reply_markup=kb.get_cancel_kb(lang), parse_mode="HTML")


@dp.message(FinanceForm.waiting_for_amount)
async def process_amount(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data['lang']
    if message.text == MESSAGES[lang]["btn_cancel"]:
        await state.clear()
        await show_menu(message, message.from_user.id, lang)
        return
    try:
        amt = float(message.text.replace(',', '.').replace(' ', ''))
        await state.update_data(amount=amt)
        if data['category'].startswith("exp_"):
            await state.set_state(FinanceForm.waiting_for_comment)
            await message.answer(MESSAGES[lang]["enter_comment"], reply_markup=kb.get_cancel_kb(lang),
                                 parse_mode="HTML")
        else:
            await finish(message, state, "-")
    except ValueError:
        await message.answer(MESSAGES[lang]["error_num"])


@dp.message(FinanceForm.waiting_for_comment)
async def process_comment(message: Message, state: FSMContext):
    await finish(message, state, message.text)


async def finish(message, state, comment):
    data = await state.get_data()
    lang = data['lang']
    cat_display = data['category']
    if cat_display.startswith("exp_"):
        cat_display = MESSAGES[lang][cat_display]
    elif cat_display in MESSAGES[lang]:
        cat_display = MESSAGES[lang]["btn_" + cat_display]

    # Сохраняем с категорией как ключом (exp_salary), а не текстом
    await db.add_transaction(message.from_user.id, EMPLOYEES[message.from_user.id], data['category'], data['amount'],
                             comment)
    await state.clear()
    await message.answer(MESSAGES[lang]["saved"].format(amount=data['amount'], category=cat_display),
                         reply_markup=kb.get_employee_kb(lang), parse_mode="HTML")


# --- ОТЧЕТЫ ---

@dp.message(lambda msg: any(msg.text == MESSAGES[l]["btn_report"] for l in MESSAGES))
async def emp_report(message: Message):
    if get_role(message.from_user.id) != "employee": return
    lang = await db.get_user_lang(message.from_user.id)
    t = MESSAGES[lang]
    loc = EMPLOYEES[message.from_user.id]
    s = await db.get_today_stats(loc)
    total = s['income'] - s['refund'] - s['expense']
    text = (
        f"{t['report_title'].format(location=loc)}\n"
        f"🗓 {db.date.today()}\n\n"
        f"{t['total_revenue']} {s['income']:,.0f} с\n"
        f"{t['total_expense']} {s['expense']:,.0f} с\n"
        f"------------------\n"
        f"{t['net_profit']} {total:,.0f} с"
    )
    await message.answer(text, parse_mode="HTML")


@dp.message(lambda msg: any(msg.text == MESSAGES[l]["btn_mgr_report"] for l in MESSAGES))
async def mgr_report(message: Message):
    if get_role(message.from_user.id) != "manager": return
    lang = await db.get_user_lang(message.from_user.id)
    t = MESSAGES[lang]
    s = await db.get_today_stats()
    total = s['income'] - s['refund'] - s['expense']
    text = (
        f"📊 <b>ВСЕ ТОЧКИ (СЕГОДНЯ)</b>\n"
        f"{t['total_revenue']} {s['income']:,.0f} с\n"
        f"{t['total_expense']} {s['expense']:,.0f} с\n"
        f"🏁 <b>ИТОГ: {total:,.0f} с</b>"
    )
    await message.answer(text, parse_mode="HTML")


@dp.message(lambda msg: any(msg.text == MESSAGES[l]["btn_analytics"] for l in MESSAGES))
async def analytics_handler(message: Message):
    if get_role(message.from_user.id) != "manager": return
    lang = await db.get_user_lang(message.from_user.id)
    t = MESSAGES[lang]
    days_names = DAYS_RU if lang == 'ru' else DAYS_EN

    per = await db.get_period_analytics()
    diff_day = per['today'] - per['yesterday']
    diff_day_pct = (diff_day / per['yesterday'] * 100) if per['yesterday'] > 0 else 0
    diff_week = per['week'] - per['prev_week']
    diff_week_pct = (diff_week / per['prev_week'] * 100) if per['prev_week'] > 0 else 0
    sign_day = "↑" if diff_day >= 0 else "↓"
    sign_week = "↑" if diff_week >= 0 else "↓"

    w_stats = await db.get_weekday_analytics()
    if w_stats:
        best = max(w_stats, key=lambda x: x[1])
        worst = min(w_stats, key=lambda x: x[1])
        best_txt = f"{days_names[best[0]]} ({best[1]:,.0f} с)"
        worst_txt = f"{days_names[worst[0]]} ({worst[1]:,.0f} с)"
    else:
        best_txt = worst_txt = "-"

    h_stats = await db.get_hourly_analytics()
    if h_stats:
        peak = max(h_stats, key=lambda x: x[1])
        dead = min(h_stats, key=lambda x: x[1])
        peak_txt = f"{peak[0]}:00"
        dead_txt = f"{dead[0]}:00"
    else:
        peak_txt = dead_txt = "-"

    exp_stats = await db.get_expense_structure()
    if exp_stats:
        top_exp = exp_stats[0]
        cat_name = MESSAGES[lang].get(top_exp[0], top_exp[0])
        exp_txt = f"{cat_name} ({top_exp[1]:,.0f} с)"
    else:
        exp_txt = "-"

    msg = (
        f"{t['analytics_title']}"
        f"{t['dyn_today']}\n"
        f"  {per['today']:,.0f} с ({sign_day} {abs(diff_day_pct):.1f}%)\n\n"
        f"{t['dyn_week']}\n"
        f"  {per['week']:,.0f} с ({sign_week} {abs(diff_week_pct):.1f}%)\n\n"
        f"➖➖➖➖➖➖\n"
        f"{t['best_day']} {best_txt}\n"
        f"{t['worst_day']} {worst_txt}\n"
        f"{t['peak_hour']} {peak_txt}\n"
        f"{t['dead_hour']} {dead_txt}\n"
        f"➖➖➖➖➖➖\n"
        f"{t['expense_top']} {exp_txt}"
    )
    await message.answer(msg, parse_mode="HTML")


@dp.message(lambda msg: any(msg.text == MESSAGES[l]["btn_excel"] for l in MESSAGES))
async def m_excel(message: Message):
    if get_role(message.from_user.id) != "manager": return
    path = await db.export_to_excel()
    if path:
        await message.answer_document(FSInputFile(path))
        os.remove(path)
    else:
        await message.answer("No Data")


@dp.message(lambda msg: any(msg.text == MESSAGES[l]["btn_ai"] for l in MESSAGES))
async def m_ai(message: Message):
    if get_role(message.from_user.id) != "manager": return
    lang = await db.get_user_lang(message.from_user.id)
    # Сообщение "Думаю..."
    await message.answer(MESSAGES[lang]["ai_thinking"], parse_mode="HTML")

    data = await db.get_weekly_summary_text()
    ai_response = await ai_service.analyze_data(data)

    try:
        await message.answer(ai_response, parse_mode="Markdown")
    except Exception:
        await message.answer(ai_response)


@dp.message(lambda msg: any(msg.text == MESSAGES[l]["btn_reset"] for l in MESSAGES))
async def m_reset(message: Message):
    if get_role(message.from_user.id) != "manager": return
    lang = await db.get_user_lang(message.from_user.id)
    await db.reset_today()
    await message.answer(MESSAGES[lang]["reset_done"])


async def main():
    await db.init_db()
    print("Bot started (Help fixed)...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped")
