from telegram.ext import Application
from apscheduler.triggers.cron import CronTrigger
from data import get_user_habits, get_all_users


async def remind_loader(application: Application):
    scheduler = application.bot_data['scheduler']
    users = await get_all_users()
    
    for user_id in users:
        habits = await get_user_habits(user_id)
        
        for habit in habits:
            time = habit["time"]
            hour, minut = map(int, time.split(":"))
            frequency = habit["frequency"]
            habit_name = habit["name"]
            if frequency == "ежедневно":
                scheduler.add_job(
                    remind_conversation,
                    CronTrigger(hour=hour, minute=minut),
                    args=[application.bot, user_id[0], habit_name],
                )
            else:
                scheduler.add_job(
                    remind_conversation,
                    CronTrigger(day_of_week=habit["frequency"],hour=hour, minute=minut),
                    args=[application.bot, user_id[0], habit_name],
                )

async def remind_conversation(bot, chat_id, habit_name):
    await bot.send_message(chat_id=chat_id, text=f"Напоминание: Пора {habit_name}!")