from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from telegram import Update
from add_habit import add_habit
import logging
from data import init_db
from show_habit import show_habits

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await init_db()
    message = await update.message.reply_text(
        "Привет! 👋\n\n"
        "Я помогу тебе управлять твоими привычками.\n\n"
        "Используй команду:\n\n"
        "🔹 /add_habit — для создания новой привычки\n"
        "🔹 /my_habits — чтобы просмотреть все свои привычки\n\n"
        "Давай начнем! 😊"
    )
    await message.pin()



if __name__ == '__main__':
    application = ApplicationBuilder().token("8100915495:AAFDv6ITyBPHY7pc7qKZuyWqkc_yG4BFkPQ").build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('my_habits', show_habits))
    add_habit(application)
    application.run_polling()
