from telegram.ext import Application
from apscheduler.triggers.cron import CronTrigger
from data import get_user_habits, get_all_users
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, CallbackQueryHandler, filters, \
    ContextTypes

data_application = []
data_habit = []


async def remind_loader(application: Application):
    data_application.append(application)
    users = await get_all_users()
    
    for user_id in users:
        habits = await get_user_habits(user_id[0])
        
        for habit in habits:
            await add_to_planer_remind(application, habit, user_id[0])
            

async def add_to_planer_remind(application, habit, user_id):
    scheduler = application.bot_data['scheduler']
    time = habit["time"]
    hour, minut = map(int, time.split(":"))
    frequency = habit["frequency"]
    habit_name = habit["name"]
    if frequency == "ежедневно":
        scheduler.add_job(
            remind_conversation,
            CronTrigger(hour=hour, minute=minut),
            args=[application, user_id, habit_name],
        )
    else:
        scheduler.add_job(
            remind_conversation,
            CronTrigger(day_of_week=habit["frequency"],hour=hour, minute=minut),
            args=[application, user_id, habit_name],
        )

async def remind_conversation(application, chat_id, habit_name):
    data_habit.append(habit_name)
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_response)],
        states={},
        fallbacks=[]
    )
    keyboard = [
        [InlineKeyboardButton("Делаю!", callback_data="do")],
        [InlineKeyboardButton("Не в этот раз!", callback_data="not_do")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await application.bot.send_message(
        chat_id=chat_id,
        text=f"Пора делать {habit_name}!",
        reply_markup=reply_markup
    )
    
    application.add_handler(conv_handler)
    
    
async def handle_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "do":
        await query.edit_message_text(text="Отлично! Продолжайте в том же духе!")
    elif query.data == "not_do":
        await query.edit_message_text(text="Не переживайте, попробуйте в следующий раз!")
    return ConversationHandler.END