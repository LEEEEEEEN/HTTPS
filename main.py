import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from telegram.ext import filters, MessageHandler, ConversationHandler, CallbackQueryHandler

from add_habit import *

# для создания логов (на случай отладки)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# описание команды /star
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_chat.send_message(
        "Привет, я бот — твой помощник по созданию привычек!"
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