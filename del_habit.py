from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from data import get_user_habits, del_user_habit, del_user_habit_stats

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

DEL = range(1)

async def delete_habit_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    habits = await get_user_habits(user_id)
    if not habits:
        await update.message.reply_text("У вас пока нет привычек для удаления.")
        return ConversationHandler.END
    message = "Какую привычку удалить? (отправьте номер привычки из списка)\n\n"
    message = create_list_habits(message, habits)
    await update.message.reply_text(message)
    return DEL

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
        await del_user_habit_stats(user_id, habit)
        habits = await get_user_habits(user_id)
        await update.message.reply_text(create_list_habits(f"Привычка \"{habit}\" была успешно удалена, вот новый список привычек:\n\n", habits))
        return ConversationHandler.END
    else:
        await update.message.reply_text(f"Нет там такого номера...\nОтправь цифру от 1 до {len(habits)}")
        return DEL

def create_list_habits(message, habits):
    for i, h in enumerate(habits, start=1):
        message += f"{i}. {h['name']} — {translate_week[h['frequency']]} в {h['time']}\n"
    return message

async def del_remind_habit(user_id, habit_name, context):
    scheduler = context.application.bot_data['scheduler']
    for job in scheduler.get_jobs():
        if len(job.args) >= 3:
            job_user_id = job.args[1]
            job_habit_name = job.args[2]
            if job_user_id == user_id and job_habit_name == habit_name:
                job.remove()

async def force_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("Диалог прерван.")
    return ConversationHandler.END


def delete_habit_handler(application):
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("delete_habit", delete_habit_start)],
        states={
            DEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, del_habit)]
        },
        fallbacks=[MessageHandler(filters.COMMAND, force_cancel)]
    )
    application.add_handler(conv_handler)
