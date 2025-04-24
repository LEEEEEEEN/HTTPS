import aiosqlite

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

