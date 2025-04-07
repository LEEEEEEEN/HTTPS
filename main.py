from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from add_habit import add_habit, show_habits

import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я помогу тебе создать привычки. Выберите одну из опций:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Создать привычку", callback_data="add_habit")],
            [InlineKeyboardButton("Посмотреть мои привычки", callback_data="my_habits")]
        ])
    )


if __name__ == '__main__':
    application = ApplicationBuilder().token("8100915495:AAFDv6ITyBPHY7pc7qKZuyWqkc_yG4BFkPQ").build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('my_habits', show_habits))
    add_habit(application)

    application.run_polling()
