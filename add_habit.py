from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters
)

NAME, FREQUENCY, TIME = range(3)

async def start_habit_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Начнем создание привычки! Как назовем её?")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    habit_name = update.message.text
    context.user_data['habit_name'] = habit_name
    
    # Создаем клавиатуру с выбором частоты
    keyboard = [
        [InlineKeyboardButton("Ежедневно", callback_data="ежедневно")],
        [InlineKeyboardButton("Раз в неделю", callback_data="раз в неделю")],
        [InlineKeyboardButton("Отмена", callback_data="отмена")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(f"Отлично! Теперь укажите, как часто вы хотите выполнять '{habit_name}':", reply_markup=reply_markup)
    return FREQUENCY


async def handle_frequency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "cancel":
        await query.edit_message_text("Создание привычки отменено.")
        return ConversationHandler.END
    
    context.user_data['frequency'] = query.data
    
    # Создаем клавиатуру с выбором времени
    keyboard = [
        [InlineKeyboardButton("08:00", callback_data="08:00"), InlineKeyboardButton("12:00", callback_data="12:00")],
        [InlineKeyboardButton("16:00", callback_data="16:00"), InlineKeyboardButton("20:00", callback_data="20:00")],
        [InlineKeyboardButton("Отмена", callback_data="cancel")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("Хорошо! Когда вам напомнить о привычке?", reply_markup=reply_markup)
    return TIME

async def handle_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "cancel":
        await query.edit_message_text("Создание привычки отменено.")
        return ConversationHandler.END
    
    context.user_data['time'] = query.data
    
    # Формируем итоговое сообщение
    habit_name = context.user_data['habit_name']
    frequency = context.user_data['frequency']
    time = context.user_data['time']
    
    await query.edit_message_text(
        f"Привычка '{habit_name}' успешно создана! Вы будете выполнять её {frequency} в {time}."
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Создание привычки отменено.")
    return ConversationHandler.END


def create_conc_handler(application):
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("add_habit", start_habit_creation)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            TIME: [CallbackQueryHandler(handle_time)],
            FREQUENCY: [CallbackQueryHandler(handle_frequency)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    application.add_handler(conv_handler)