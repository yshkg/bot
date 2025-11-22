import aiosqlite
import pandas as pd
from datetime import date, datetime, timedelta
from config import DB_NAME


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                location TEXT,
                category TEXT,
                amount REAL,
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                language TEXT DEFAULT 'ru'
            )
        """)
        await db.commit()


# --- ЯЗЫК ---
async def set_user_lang(user_id: int, lang: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT INTO users (user_id, language) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET language=excluded.language",
            (user_id, lang)
        )
        await db.commit()


async def get_user_lang(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        return row[0] if row else "ru"


# --- ТРАНЗАКЦИИ ---
async def add_transaction(user_id: int, location: str, category: str, amount: float, comment: str = None):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT INTO transactions (user_id, location, category, amount, comment) VALUES (?, ?, ?, ?, ?)",
            (user_id, location, category, amount, comment)
        )
        await db.commit()


async def get_today_stats(location: str = None):
    """Статистика за сегодня (для отчетов)."""
    today = date.today()
    query = "SELECT category, SUM(amount) FROM transactions WHERE date(created_at) = ?"
    params = [today]
    if location:
        query += " AND location = ?"
        params.append(location)
    query += " GROUP BY category"

    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()

    # Суммируем расходы (все категории, начинающиеся на exp_)
    stats = {"income": 0.0, "expense": 0.0, "refund": 0.0, "checks": 0}

    for cat, amount in rows:
        if cat in ['cash', 'card', 'qr']:
            stats["income"] += amount
        elif cat.startswith('exp_'):
            stats["expense"] += amount
        elif cat == 'refund':
            stats["refund"] += amount
        elif cat == 'checks':
            stats["checks"] += amount

    return stats


# --- АНАЛИТИКА (НОВОЕ) ---

async def get_period_analytics():
    """Сравнивает сегодня/вчера и неделю/прошлую неделю."""
    async with aiosqlite.connect(DB_NAME) as db:
        # 1. Сегодня vs Вчера
        cursor = await db.execute("""
            SELECT 
                SUM(CASE WHEN date(created_at) = date('now') THEN amount ELSE 0 END) as today,
                SUM(CASE WHEN date(created_at) = date('now', '-1 day') THEN amount ELSE 0 END) as yesterday
            FROM transactions WHERE category IN ('cash', 'card', 'qr')
        """)
        day_row = await cursor.fetchone()

        # 2. 7 дней vs Пред. 7 дней
        cursor = await db.execute("""
            SELECT 
                SUM(CASE WHEN created_at >= date('now', '-7 days') THEN amount ELSE 0 END) as last_7,
                SUM(CASE WHEN created_at >= date('now', '-14 days') AND created_at < date('now', '-7 days') THEN amount ELSE 0 END) as prev_7
            FROM transactions WHERE category IN ('cash', 'card', 'qr')
        """)
        week_row = await cursor.fetchone()

    return {
        "today": day_row[0] or 0,
        "yesterday": day_row[1] or 0,
        "week": week_row[0] or 0,
        "prev_week": week_row[1] or 0
    }


async def get_weekday_analytics():
    """Лучший и худший день недели."""
    # strftime('%w') возвращает 0=Воскресенье, 1=Понедельник...
    query = """
        SELECT strftime('%w', created_at) as wday, SUM(amount), COUNT(DISTINCT date(created_at))
        FROM transactions 
        WHERE category IN ('cash', 'card', 'qr')
        GROUP BY wday
    """
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(query)
        rows = await cursor.fetchall()

    # Преобразуем в среднюю выручку (Сумма / кол-во таких дней в базе)
    # Чтобы один удачный понедельник не перекосил статистику
    results = []
    for wday, total, count in rows:
        avg = total / count if count > 0 else 0
        results.append((int(wday), avg))

    return results


async def get_hourly_analytics():
    """Пиковые часы."""
    query = """
        SELECT strftime('%H', created_at) as hour, SUM(amount)
        FROM transactions 
        WHERE category IN ('cash', 'card', 'qr')
        GROUP BY hour
        ORDER BY hour
    """
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(query)
        rows = await cursor.fetchall()  # [(09, 5000), (10, 2000)...]
    return rows


async def get_expense_structure():
    """Структура расходов за месяц."""
    query = """
        SELECT category, SUM(amount)
        FROM transactions 
        WHERE category LIKE 'exp_%' AND created_at >= date('now', 'start of month')
        GROUP BY category
        ORDER BY SUM(amount) DESC
    """
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(query)
        rows = await cursor.fetchall()
    return rows


async def get_weekly_summary_text():
    """Для AI (текстовый формат)."""
    query = """
        SELECT date(created_at), category, SUM(amount)
        FROM transactions 
        WHERE created_at >= date('now', '-7 days')
        GROUP BY date(created_at), category
    """
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(query)
        rows = await cursor.fetchall()

    text = ""
    for d, c, a in rows:
        text += f"{d}: {c} = {a}\n"
    return text


async def export_to_excel():
    async with aiosqlite.connect(DB_NAME) as db:
        query = "SELECT location, category, amount, comment, created_at FROM transactions ORDER BY created_at DESC"
        async with db.execute(query) as cursor:
            cols = [d[0] for d in cursor.description]
            rows = await cursor.fetchall()

    if not rows: return None
    df = pd.DataFrame(rows, columns=cols)
    path = f"full_report_{date.today()}.xlsx"
    df.to_excel(path, index=False)
    return path


async def reset_today():
    today = date.today()
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM transactions WHERE date(created_at) = ?", (today,))
        await db.commit()
