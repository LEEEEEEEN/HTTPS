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

# описание команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="Привет, я бот - твой помощник по созданию привычек!")


async def add_habit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Введите название вашей привычки")
    habit_name = ' '.join(context.args)

    
async def remove_habit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

async def see_habits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

# запуск хостинга
if __name__ == '__main__':
    application = ApplicationBuilder().token("8100915495:AAFDv6ITyBPHY7pc7qKZuyWqkc_yG4BFkPQ").build()
    
    start_handler = CommandHandler('start', start)
    
    create_conc_handler(application)
    application.add_handler(start_handler)
    
    application.run_polling() # while True