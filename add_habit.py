from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import (
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CommandHandler,
    filters,
)

# Состояния
NAME, HOUR = range(2)

async def start_habit_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Как назовём привычку?")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    habit_name = update.message.text
    context.user_data['habit_name'] = habit_name

    keyboard = [
        [InlineKeyboardButton(f"{str(h).zfill(2)}:00", callback_data=str(h)) for h in range(0, 24, 3)],
        [InlineKeyboardButton("Отмена", callback_data="отмена")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Когда напоминать каждый день для привычки «{habit_name}»?",
        reply_markup=reply_markup
    )
    return HOUR

async def handle_hour(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "отмена":
        return await cancel_conversation(update)

    context.user_data['hour'] = query.data

    habit_name = context.user_data['habit_name']
    hour = context.user_data['hour']

    await query.edit_message_text(
        f"Привычка «{habit_name}» успешно создана! Я напомню тебе каждый день в {hour}:00."
    )
    return ConversationHandler.END

async def cancel_conversation(update: Update):
    if update.callback_query:
        await update.callback_query.message.edit_text("Создание привычки отменено.")
    else:
        await update.message.reply_text("Создание привычки отменено.")
    return ConversationHandler.END

def add_habit(application):
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & filters.Regex("^Завести привычку$"), start_habit_creation)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            HOUR: [CallbackQueryHandler(handle_hour)],
        },
        fallbacks=[CommandHandler("cancel", cancel_conversation)],
    )

    application.add_handler(conv_handler)
