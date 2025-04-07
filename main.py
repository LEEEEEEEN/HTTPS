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
        ["Завести привычку"],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Привет, я бот — твой помощник по созданию привычек!\nВыбери, что хочешь сделать:",
        reply_markup=reply_markup
    )

    
async def remove_habit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

async def see_habits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

# запуск хостинга
if __name__ == '__main__':
    application = ApplicationBuilder().token("8100915495:AAFDv6ITyBPHY7pc7qKZuyWqkc_yG4BFkPQ").build()
    
    start_handler = CommandHandler('start', start)
    
    add_habit(application)
    application.add_handler(start_handler)
    
    application.run_polling() # while True