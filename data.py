import aiosqlite
from datetime import datetime

DB_PATH = "data/data.db"
DB_USERS_PATH = "data/users_habits.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS habits (
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                frequency TEXT NOT NULL,
                time TEXT NOT NULL
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER NOT NULL
            )
        ''')
        await db.commit()
    async with aiosqlite.connect(DB_USERS_PATH) as db:
        await db.commit()
        
async def save_habit(user_id: int, habit: dict):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT INTO habits (user_id, name, frequency, time)
            VALUES (?, ?, ?, ?)
        ''', (user_id, habit["name"], habit["frequency"], habit["time"]))
        await db.commit()
    
async def save_user(user_id):
    if user_id not in [id[0] for id in await get_all_users()]:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute('''
                INSERT INTO users (user_id)
                VALUES (?)
            ''', (user_id,))
            await db.commit()
    
async def get_all_users():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('''
            SELECT user_id FROM users
        ''') as cursor:
            return await cursor.fetchall()
        
async def del_user_habit(user_id, habit_name):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            '''DELETE FROM habits WHERE user_id = ? AND name = ?''',
            (user_id, habit_name)
        )
        await db.commit()

async def get_user_habits(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('''
            SELECT name, frequency, time FROM habits WHERE user_id = ?
        ''', (user_id,)) as cursor:
            rows = await cursor.fetchall()
            return [{"name": row[0], "frequency": row[1], "time": row[2]} for row in rows]

async def init_user_habits_table(user_id):
    async with aiosqlite.connect(DB_USERS_PATH) as db:
        await db.execute(f'''
            CREATE TABLE IF NOT EXISTS "user_{user_id}" (
                date TEXT NOT NULL,
                name TEXT NOT NULL,
                frequency TEXT NOT NULL,
                status INT NOT NULL
            )
        ''')
        await db.commit()

async def save_user_habit(user_id, habit_name, status):
    h = None
    for habit in await get_user_habits(user_id):
        if habit['name'] == habit_name:
            h = habit
            break
    today = datetime.now().strftime("%Y-%m-%d")
    if h:
        async with aiosqlite.connect(DB_USERS_PATH) as db:
            await db.execute(f'''
                    INSERT INTO user_{user_id} (date, name, frequency, status)
                    VALUES (?, ?, ?, ?)
                ''', (today, h['name'], h['frequency'], status))
            await db.commit()
    else:
        raise ValueError(f"Привычка с именем '{habit_name}' не найдена для пользователя {user_id}.")

async def get_habit_stats(user_id, habit_name):
    async with aiosqlite.connect("data/users_habits.db") as db:
        async with db.execute(f'''
            SELECT date, status FROM user_{user_id}
            WHERE name = ?
            ORDER BY date
        ''', (habit_name,)) as cursor:
            rows = await cursor.fetchall()
            stats = {}
            for date, status in rows:
                if date not in stats:
                    stats[date] = {"total": 0, "success": 0}
                stats[date]["total"] += 1
                stats[date]["success"] += status
            dates = sorted(stats.keys())
            success_rates = [
                round((stats[date]["success"] / stats[date]["total"]) * 100, 1)
                for date in dates
            ]
            return dates, success_rates

async def del_user_habit_stats(user_id, habit_name):
    async with aiosqlite.connect(DB_USERS_PATH) as db:
        await db.execute(f'''
            DELETE FROM user_{user_id}
            WHERE name = ?
        ''', (habit_name,))
        await db.commit()