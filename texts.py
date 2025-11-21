MESSAGES = {
    "ru": {
        "choose_lang": "🌍 Выберите язык системы / Choose system language:",
        "lang_changed": "🇷🇺 Язык изменен на Русский.",
        "welcome_manager": "👋 <b>Добрый день, Руководитель.</b>\nСистема готова к работе. Выберите действие:",
        "welcome_employee": "👋 <b>Смена открыта.</b>\nОбъект: <b>{point}</b>\n\nВыберите категорию для внесения данных:",
        "access_denied": "⛔ <b>Доступ запрещен.</b>\nВаш ID не найден в списке сотрудников.",
        "input_amount": "👇 <b>Введите сумму:</b>\n(Например: 5000 или 1250.50)",
        "input_comment": "🖊 <b>Укажите назначение платежа:</b>\n(Например: Такси, Вода, Закупка)",
        "saved": "✅ <b>Принято:</b> {amount} ({category})",
        "error_digit": "⚠ <b>Ошибка ввода.</b>\nПожалуйста, введите число.",
        "cancelled": "❌ Операция отменена.",
        "report_title": "📊 <b>ФИНАНСОВЫЙ ОТЧЁТ: {location}</b>",
        "report_generated": "⏳ Формирую Excel-файл...",
        "reset_done": "🗑 <b>Смена закрыта.</b> Данные за сегодня обнулены.",
        "no_data": "⚠ Данных за сегодня пока нет.",

        # Названия кнопок
        "btn_cash": "💵 Наличные",
        "btn_card": "💳 Карта",
        "btn_qr": "📱 QR / Перевод",
        "btn_checks": "🧾 Чеки (кол-во)",
        "btn_refund": "🔙 Возврат",
        "btn_expense": "📤 Расход / Инкассация",
        "btn_report": "📊 Мой отчёт",
        "btn_mgr_report": "📊 Отчёт за сегодня",
        "btn_excel": "📥 Скачать Excel",
        "btn_reset": "🗑 Закрыть смену (Сброс)",
        "btn_help": "🆘 Помощь",
        "btn_cancel": "❌ Отмена",

        # Текст справки
        "help_text_employee": (
            "📋 <b>ИНСТРУКЦИЯ СОТРУДНИКА</b>\n\n"
            "1. <b>Внесение выручки:</b> Нажмите категорию (Нал/Карта) и введите сумму.\n"
            "2. <b>Ошибка ввода:</b> Введите сумму со знаком минус (пример: -500), чтобы вычесть её.\n"
            "3. <b>Расходы:</b> При нажатии 'Расход' бот запросит комментарий (на что ушли деньги).\n"
            "4. <b>Отчет:</b> Кнопка 'Мой отчёт' показывает вашу текущую кассу."
        ),
        "help_text_manager": (
            "💼 <b>ИНСТРУКЦИЯ РУКОВОДИТЕЛЯ</b>\n\n"
            "1. <b>Отчёт за сегодня:</b> Быстрая сводка выручки в чате.\n"
            "2. <b>Скачать Excel:</b> Полная выгрузка всех операций с комментариями и временем.\n"
            "3. <b>Закрыть смену:</b> Удаляет все данные за текущий день. Нажимать в конце дня или утром."
        )
    },
    "en": {
        "choose_lang": "🌍 Please choose language:",
        "lang_changed": "🇬🇧 Language set to English.",
        "welcome_manager": "👋 <b>Welcome, Manager.</b>\nSystem ready. Choose action:",
        "welcome_employee": "👋 <b>Shift started.</b>\nLocation: <b>{point}</b>\n\nSelect category:",
        "access_denied": "⛔ <b>Access denied.</b>",
        "input_amount": "👇 <b>Enter amount:</b>",
        "input_comment": "🖊 <b>Enter comment:</b>",
        "saved": "✅ <b>Saved:</b> {amount} ({category})",
        "error_digit": "⚠ <b>Error.</b> Please enter a number.",
        "cancelled": "❌ Cancelled.",
        "report_title": "📊 <b>REPORT: {location}</b>",
        "report_generated": "⏳ Generating Excel...",
        "reset_done": "🗑 <b>Shift closed.</b> Data reset.",
        "no_data": "⚠ No data found.",

        # Buttons
        "btn_cash": "💵 Cash",
        "btn_card": "💳 Card",
        "btn_qr": "📱 QR / Transfer",
        "btn_checks": "🧾 Checks (qty)",
        "btn_refund": "🔙 Refund",
        "btn_expense": "📤 Expense",
        "btn_report": "📊 My Report",
        "btn_mgr_report": "📊 Today's Report",
        "btn_excel": "📥 Download Excel",
        "btn_reset": "🗑 Close Shift (Reset)",
        "btn_help": "🆘 Help",
        "btn_cancel": "❌ Cancel",

        # Help
        "help_text_employee": (
            "📋 <b>EMPLOYEE GUIDE</b>\n\n"
            "1. Select category and enter amount.\n"
            "2. To fix mistake, enter negative number (e.g. -500).\n"
            "3. Expenses require a comment.\n"
        ),
        "help_text_manager": (
            "💼 <b>MANAGER GUIDE</b>\n\n"
            "1. <b>Today's Report:</b> Quick summary.\n"
            "2. <b>Download Excel:</b> Full history export.\n"
            "3. <b>Close Shift:</b> Resets all data for today."
        )
    }
}
