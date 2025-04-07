import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from telegram.ext import filters, MessageHandler, ConversationHandler, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup
from add_habit import *

# для создания логов (на случай отладки)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["Завести привычку", "Мои привычки"],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Привет, я бот — твой помощник по созданию привычек!\nВыбери, что хочешь сделать:",
        reply_markup=reply_markup
    )


async def see_habits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    habits = user_habits.get(user_id, [])

    if not habits:
        await update.message.reply_text("У вас пока нет привычек.")
        return

    message = "Ваши привычки:\n\n"
    for i, h in enumerate(habits, start=1):
        message += f"{i}. {h['name']} — {h['frequency']} в {h['time']}\n"

    await update.message.reply_text(message)


# запуск хостинга
if __name__ == '__main__':
    application = ApplicationBuilder().token("8100915495:AAFDv6ITyBPHY7pc7qKZuyWqkc_yG4BFkPQ").build()

    start_handler = CommandHandler('start', start)
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^Завести привычку$"), start_habit_creation))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^Мои привычки$"), see_habits))

    add_habit(application)
    application.add_handler(start_handler)

    application.run_polling()  # while True
