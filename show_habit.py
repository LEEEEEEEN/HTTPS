from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from data import get_user_habits
import requests
from bs4 import BeautifulSoup

def get_joke():
    url = "https://nekdo.ru/random/ "
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        joke_div = soup.select_one('.text')

        if joke_div:
            for br in joke_div.find_all("br"):
                br.replace_with("\n")
            return joke_div.get_text(strip=True)
        else:
            return "Сегодня без шуток 😕"

    except Exception as e:
        print("Ошибка получения шутки:", e)
        return "Сегодня без шуток 😢"

translate_week = {
    "mon": "каждый понедельник",
    "tue": "каждый вторник",
    "wed": "каждую среду",
    "thu": "каждый четверг",
    "fri": "каждую пятницу",
    "sat": "каждую субботу",
    "sun": "каждое воскресенье",
    "ежедневно": "ежедневно"
}

def create_list_habits(message, habits):
    for i, h in enumerate(habits, start=1):
        message += f"{i}. {h['name']} — {translate_week[h['frequency']]} в {h['time']}\n"
    return message

async def show_habits_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    habits = await get_user_habits(user_id)
    if not habits:
        await update.message.reply_text("У вас пока нет привычек.")
        return
    message = "Ваши привычки:\n\n"
    message = create_list_habits(message, habits)
    joke = get_joke()
    await update.message.reply_text(message + f"\nКстати, {joke[0].lower()}{joke[1:]}")

def show_habit_handler(application):
    application.add_handler(CommandHandler("my_habits", show_habits_start))