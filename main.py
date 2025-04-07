from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from add_habit import add_habit, start_habit_creation, show_habits  # Импортируем start_habit_creation

import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Начальное приветствие и выбор
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["Создать привычку", "Мои привычки"],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Привет! Я помогу тебе создать и следить за привычками. Выбери, что ты хочешь сделать:",
        reply_markup=reply_markup
    )

async def handle_create_habit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Начнем создание привычки! Как назовем её?", reply_markup=ReplyKeyboardMarkup([[]]))
    return await start_habit_creation(update, context)

if __name__ == '__main__':
    application = ApplicationBuilder().token("8100915495:AAFDv6ITyBPHY7pc7qKZuyWqkc_yG4BFkPQ").build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^Создать привычку$"), handle_create_habit))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^Мои привычки$"), show_habits))
    add_habit(application)

    application.run_polling()
