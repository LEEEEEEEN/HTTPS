from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from add_habit import add_habit, show_habits

import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Используй команду /add_habit, чтобы начать создание привычки или /my_habits для просмотра привычек."
    )

if __name__ == '__main__':
    application = ApplicationBuilder().token("8100915495:AAFDv6ITyBPHY7pc7qKZuyWqkc_yG4BFkPQ").build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('my_habits', show_habits))

    add_habit(application)

    application.run_polling()
