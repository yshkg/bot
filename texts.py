MESSAGES = {
    "ru": {
        "choose_lang": "🌍 Выберите язык / Choose language:",
        "lang_changed": "🇷🇺 Язык изменен на Русский.",
        "welcome_manager": "📊 <b>Панель управления</b>\nДобро пожаловать в систему финансового учета.",
        "welcome_employee": "📍 Точка: <b>{point}</b>\nСмена открыта. Ожидание операций...",
        "access_denied": "⛔ У вас нет доступа к этой системе.",

        "enter_amount": "👇 <b>Введите сумму (сом):</b>",
        "enter_comment": "🖊 <b>Напишите комментарий:</b>\n(Например: Такси, Обед, Закуп)",
        "choose_category": "📂 Выберите категорию расхода:",

        "saved": "✅ <b>Принято:</b> {amount} с ({category})",
        "error_num": "⚠ Ошибка. Введите число (например: 500).",
        "cancelled": "❌ Отмена.",

        # Отчеты и статусы
        "report_title": "📊 <b>СВОДКА: {location}</b>",
        "total_revenue": "➕ Выручка:",
        "total_expense": "➖ Расходы:",
        "net_profit": "💰 <b>ИТОГ В КАССЕ:</b>",
        "checks_count": "🧾 Чеков:",
        "no_data": "⚠ Данных пока нет.",
        "reset_done": "🗑 <b>Смена закрыта.</b> Данные обнулены.",

        # --- ВОТ ЭТИ СТРОКИ ПРОПАЛИ, ВОЗВРАЩАЕМ ИХ ---
        "ai_thinking": "🧠 <b>ИИ анализирует данные...</b>\nПожалуйста, подождите пару секунд.",
        "report_generated": "⏳ <b>Формирую Excel-файл...</b>",
        # ---------------------------------------------

        # Аналитика
        "analytics_title": "📈 <b>ГЛУБОКАЯ АНАЛИТИКА</b>\n\n",
        "dyn_today": "📆 <b>Сегодня vs Вчера:</b>",
        "dyn_week": "🗓 <b>Неделя vs Прошлая:</b>",
        "best_day": "🏆 Лучший день:",
        "worst_day": "📉 Худший день:",
        "peak_hour": "⏰ Час-пик:",
        "dead_hour": "💤 Мертвый час:",
        "expense_top": "💸 Главный расход:",

        # Кнопки
        "btn_cash": "💵 Нал",
        "btn_card": "💳 Карта",
        "btn_qr": "📱 QR",
        "btn_checks": "🧾 Чеки",
        "btn_refund": "🔙 Возврат",
        "btn_expense": "📤 РАСХОД",

        "btn_report": "📊 Мой отчёт",
        "btn_mgr_report": "📊 Отчёт дня",
        "btn_analytics": "📈 Аналитика",
        "btn_excel": "📥 Excel",
        "btn_ai": "🧠 AI Совет",
        "btn_reset": "🗑 СБРОС ДНЯ",
        "btn_lang": "🌍 Язык",
        "btn_help": "🆘 Помощь",
        "btn_cancel": "❌ Отмена",

        "exp_salary": "👷‍♂️ Зарплата",
        "exp_rent": "🏠 Аренда",
        "exp_products": "🍎 Продукты",
        "exp_supplies": "🧹 Хоз. нужды",
        "exp_other": "📝 Прочее",

        # Текст справки
        "help_header": "🤖 <b>О ПРОЕКТЕ: Finance Bot v2.0</b>\n\nЭто система автоматизации кассы и аналитики.\n\n",

        "help_employee": (
            "👨‍🔧 <b>ИНСТРУКЦИЯ СОТРУДНИКА</b>\n\n"
            "✅ <b>Выручка:</b> Нажмите [💵 Нал] / [💳 Карта] и введите сумму.\n"
            "📤 <b>Расход:</b> Нажмите [📤 РАСХОД], выберите категорию и введите сумму.\n"
            "📊 <b>Сверка:</b> Нажмите [📊 Мой отчёт] чтобы проверить кассу."
        ),

        "help_manager": (
            "👨‍💼 <b>ИНСТРУКЦИЯ РУКОВОДИТЕЛЯ</b>\n\n"
            "📊 <b>Отчёты:</b> [Отчёт дня] (сводка) и [📈 Аналитика] (тренды).\n"
            "🧠 <b>AI:</b> [🧠 AI Совет] — анализ недели нейросетью.\n"
            "⚙️ <b>Смена:</b> [🗑 СБРОС ДНЯ] — обнулить кассу (делать в конце дня)."
        )
    },
    "en": {
        "choose_lang": "🌍 Choose language:",
        "lang_changed": "🇬🇧 Language set to English.",
        "welcome_manager": "📊 <b>Manager Panel</b>",
        "welcome_employee": "📍 Point: <b>{point}</b>",
        "access_denied": "⛔ Access denied.",

        "enter_amount": "👇 <b>Enter amount (som):</b>",
        "enter_comment": "🖊 <b>Enter comment:</b>",
        "choose_category": "📂 Select category:",

        "saved": "✅ <b>Saved:</b> {amount} c ({category})",
        "error_num": "⚠ Error. Not a number.",
        "cancelled": "❌ Cancelled.",

        "report_title": "📊 <b>REPORT: {location}</b>",
        "total_revenue": "➕ Revenue:",
        "total_expense": "➖ Expenses:",
        "net_profit": "💰 <b>NET CASH:</b>",
        "checks_count": "🧾 Checks:",
        "no_data": "⚠ No data.",
        "reset_done": "🗑 <b>Shift closed.</b> Data reset.",

        # --- MISSING LINES RETURNED ---
        "ai_thinking": "🧠 <b>AI is analyzing data...</b>\nPlease wait.",
        "report_generated": "⏳ <b>Generating Excel...</b>",
        # ------------------------------

        "analytics_title": "📈 <b>DEEP ANALYTICS</b>\n\n",
        "dyn_today": "📆 <b>Today vs Yest:</b>",
        "dyn_week": "🗓 <b>Week vs Prev:</b>",
        "best_day": "🏆 Best Day:",
        "worst_day": "📉 Worst Day:",
        "peak_hour": "⏰ Peak Hour:",
        "dead_hour": "💤 Dead Hour:",
        "expense_top": "💸 Top Expense:",

        "btn_cash": "💵 Cash",
        "btn_card": "💳 Card",
        "btn_qr": "📱 QR",
        "btn_checks": "🧾 Checks",
        "btn_refund": "🔙 Refund",
        "btn_expense": "📤 EXPENSE",

        "btn_report": "📊 My Report",
        "btn_mgr_report": "📊 Daily Report",
        "btn_analytics": "📈 Analytics",
        "btn_excel": "📥 Excel",
        "btn_ai": "🧠 AI Advice",
        "btn_reset": "🗑 RESET DAY",
        "btn_lang": "🌍 Lang",
        "btn_help": "🆘 Help",
        "btn_cancel": "❌ Cancel",

        "exp_salary": "👷‍♂️ Salary",
        "exp_rent": "🏠 Rent",
        "exp_products": "🍎 Products",
        "exp_supplies": "🧹 Supplies",
        "exp_other": "📝 Other",

        "help_header": "🤖 <b>ABOUT: Finance Bot v2.0</b>\n\n",
        "help_employee": (
            "👨‍🔧 <b>EMPLOYEE GUIDE</b>\n\n"
            "✅ <b>Income:</b> Tap Cash/Card/QR and enter amount.\n"
            "📤 <b>Expense:</b> Tap EXPENSE, choose category.\n"
            "📊 <b>Report:</b> Tap 'My Report'."
        ),
        "help_manager": (
            "👨‍💼 <b>MANAGER GUIDE</b>\n\n"
            "📊 <b>Reports:</b> Daily stats & Deep analytics.\n"
            "🧠 <b>AI:</b> Get business advice.\n"
            "⚙️ <b>Reset:</b> Use 'RESET DAY' to close the shift."
        )
    }
}

# Списки дней
DAYS_RU = ["Воскресенье", "Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]
DAYS_EN = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
