from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, CallbackQueryHandler, filters, \
    ContextTypes
from data import get_user_habits, del_user_habit
from add_habit import start_habit_creation


translate_week = {
    "mon": "каждый понедельник",
    "tue": "каждый вторник",
    "wed": "каждую среду",
    "thu": "каждый четверг",
    "fri": "каждую пятницу",
    "sat": "каждую субботу",
    "sun": "каждое воскресенье",
    "ежедневно": "ежедневно"
}

SHOW, DEL, STATS = range(3)

def create_list_habits(message, habits):
    for i, h in enumerate(habits, start=1):
            message += f"{i}. {h['name']} — {translate_week[h['frequency']]} в {h['time']}\n"
    return message

def check_number_dumb():
    pass

async def show_habits_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    habits = await get_user_habits(user_id)
    if not habits:
        await update.message.reply_text("У вас пока нет привычек.")
        return
    keyboard = []
    
    message = "Ваши привычки:\n\n"
    for i, h in enumerate(habits, start=1):
        message += f"{i}. {h['name']} — {translate_week[h['frequency']]} в {h['time']}\n"
    
    
    keyboard.append([InlineKeyboardButton("Показать статистику", callback_data = "stats"),
                     InlineKeyboardButton("Удалить привычку", callback_data = "del")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(message, reply_markup=reply_markup)
    
    return SHOW

async def del_habit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    habit = ""
    habits = await get_user_habits(user_id)
    if update.message.text.isdigit() and 0 < int(update.message.text) <= len(habits):
        for i, h in enumerate(habits, start=1):
            if str(i) == update.message.text:
                habit = h["name"]
        await del_user_habit(user_id, habit)
        await del_remind_habit(user_id, habit, context=context)
        habits = await get_user_habits(user_id)
        await update.message.reply_text(create_list_habits(f"Привычка \"{habit}\" была успешно удалена, вот новый список привычек:\n\n", habits))
        return ConversationHandler.END
    else:
        await update.message.reply_text(f"Нет там такого номера...\nОтправь цифру от 1 до {len(habits)}")
        return DEL

async def del_remind_habit(user_id, habit_name, context):
    scheduler = context.application.bot_data['scheduler']
    for job in scheduler.get_jobs():
        if len(job.args) >= 3:
            job_user_id = job.args[1]
            job_habit_name = job.args[2]
            if job_user_id == user_id and job_habit_name == habit_name:
                job.remove()
    
async def stats_habits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.message.text)

async def show_habits_show(update: Update, context: ContextTypes.DEFAULT_TYPE):    
    callback = update.callback_query
    user_id = update.effective_user.id
    habits = await get_user_habits(user_id)
    
    await callback.answer()
    
    if callback.data == "stats":
        message = create_list_habits("0. По всем привычкам\n", habits)
        await callback.edit_message_text("По какой привычке вывести статистику? (отправьте номер привычки из списка)\n\n" + message)
        return STATS
    elif callback.data == "del":
        message = create_list_habits("", habits)
        await callback.edit_message_text("Какую привычку удалить? (отправьте номер привычки из списка)\n\n" + message)
        return DEL
    return ConversationHandler.END 

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("Отмена.")
    return ConversationHandler.END

async def handle_wrong_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Используйте кнопки для выбора действия.")
    return SHOW


async def force_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Сбрасываем состояние
    context.user_data.clear()
    await update.message.reply_text("Диалог прерван, повторите последнее действие если это была команда.")
    return ConversationHandler.END


def show_habits(application):
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("my_habits", show_habits_start)],
        states={
            SHOW: [CallbackQueryHandler(show_habits_show),
                   MessageHandler(filters.TEXT & ~filters.COMMAND, handle_wrong_input)],
            STATS: [MessageHandler(filters.TEXT & ~filters.COMMAND, stats_habits)],
            DEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, del_habit)]
        },
        fallbacks=[CommandHandler("cancel", cancel),
                   CommandHandler("add_habit", start_habit_creation),
                   CommandHandler("start", force_cancel),
                   MessageHandler(filters.COMMAND, force_cancel)],
    )
    application.add_handler(conv_handler)