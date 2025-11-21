import aiosqlite
import pandas as pd
from datetime import date
import os
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
        return row[0] if row else None


async def add_transaction(user_id: int, location: str, category: str, amount: float, comment: str = None):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT INTO transactions (user_id, location, category, amount, comment) VALUES (?, ?, ?, ?, ?)",
            (user_id, location, category, amount, comment)
        )
        await db.commit()


async def get_today_stats(location: str = None):
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

    stats = {"cash": 0.0, "card": 0.0, "qr": 0.0, "refund": 0.0, "expense": 0.0, "checks": 0}
    for category, total in rows:
        if category in stats:
            stats[category] = total
    return stats


async def export_to_excel():
    async with aiosqlite.connect(DB_NAME) as db:
        query = "SELECT id, location, category, amount, comment, created_at FROM transactions ORDER BY created_at DESC"
        async with db.execute(query) as cursor:
            columns = [d[0] for d in cursor.description]
            rows = await cursor.fetchall()

    if not rows: return None
    df = pd.DataFrame(rows, columns=columns)
    file_path = f"report_{date.today()}.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


async def reset_today():
    today = date.today()
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM transactions WHERE date(created_at) = ?", (today,))
        await db.commit()
