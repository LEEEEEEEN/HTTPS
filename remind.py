from telegram.ext import Application
from apscheduler.triggers.cron import CronTrigger
from data import get_user_habits, get_all_users, save_user_habit
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CallbackQueryHandler, filters, \
    ContextTypes

data_application = []


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
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_response)],
        states={},
        fallbacks=[],
        per_message=False
    )
    keyboard = [
        [InlineKeyboardButton("Делаю!", callback_data=f"do {habit_name}")],
        [InlineKeyboardButton("Не в этот раз!", callback_data=f"not_do {habit_name}")]
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
    status = 0
    text_status, habit_name = query.data.split()
    print(text_status, habit_name)
    if text_status == "do":
        await query.edit_message_text(text="Отлично! Продолжайте в том же духе!")
        status = 1
    elif text_status == "not_do":
        await query.edit_message_text(text="Не переживайте, попробуйте в следующий раз!")
    
    await save_user_habit(update.effective_user.id, habit_name, status)
    
    return ConversationHandler.END