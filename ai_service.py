import google.generativeai as genai
from config import GOOGLE_API_KEY

# Глобальная переменная для модели
ai_model = None


def setup_model():
    """
    Автоматически ищет доступную модель Gemini.
    """
    global ai_model
    try:
        genai.configure(api_key=GOOGLE_API_KEY)

        # 1. Получаем список всех моделей, доступных ВАШЕМУ ключу
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)

        # 2. Пытаемся выбрать лучшую из доступных
        # Приоритет: Flash (быстрая) -> Pro (умная) -> Любая другая Gemini
        chosen_model_name = None

        # Ищем Flash
        for m in available_models:
            if "flash" in m:
                chosen_model_name = m
                break

        # Если Flash нет, ищем Pro
        if not chosen_model_name:
            for m in available_models:
                if "pro" in m:
                    chosen_model_name = m
                    break

        # Если вообще ничего похожего, берем первую попавшуюся
        if not chosen_model_name and available_models:
            chosen_model_name = available_models[0]

        if chosen_model_name:
            print(f"✅ AI успешно подключен. Используем модель: {chosen_model_name}")
            ai_model = genai.GenerativeModel(chosen_model_name)
        else:
            print("❌ AI ошибка: Список доступных моделей пуст (проверьте VPN).")
            ai_model = None

    except Exception as e:
        print(f"❌ Ошибка настройки AI: {e}")
        ai_model = None


# Запускаем настройку сразу при импорте
setup_model()


async def analyze_data(report_text: str):
    if not ai_model:
        # Пробуем переподключиться, если в первый раз не вышло
        setup_model()
        if not ai_model:
            return "⚠ Ошибка: AI недоступен. Проверьте VPN и перезапустите бота."

    if not report_text or "Нет данных" in report_text:
        return "⚠ Недостаточно данных для анализа."

    prompt = (
        "Ты — финансовый директор. Проанализируй отчет о продажах за неделю.\n"
        "ВАЖНО: Валюта отчета — Кыргызский сом (с). Все суммы пиши в сомах.\n"  # <--- ДОБАВИЛИ ЭТУ СТРОКУ
        f"Данные:\n{report_text}\n\n"
        "Задача:\n"
        "1. Лучший день по выручке.\n"
        "2. Есть ли странные расходы?\n"
        "3. Совет бизнесу.\n"
        "Ответь кратко на русском, используй эмодзи. Без * #"
    )

    try:
        response = ai_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠ Ошибка генерации: {e}"
