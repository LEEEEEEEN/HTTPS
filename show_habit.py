from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, CallbackQueryHandler, filters, \
    ContextTypes
from data import get_user_habits



async def show_habits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    habits = await get_user_habits(user_id)
    print("DEBUG: Habits:", habits)
    if not habits:
        await update.message.reply_text("У вас пока нет привычек.")
        return

    message = "Ваши привычки:\n\n"
    for i, h in enumerate(habits, start=1):
        message += f"{i}. {h['name']} — {h['frequency']} в {h['time']}\n"

    await update.message.reply_text(message)