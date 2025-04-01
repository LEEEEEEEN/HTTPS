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
    context.user_data['habit_name'] = habit_name #сохранение в временный словарь во время диалога
    
    # Создаем клавиатуру с выбором частоты
    keyboard = [
        [InlineKeyboardButton("Ежедневно", callback_data="ежедневно")],
        [InlineKeyboardButton("Раз в неделю", callback_data="раз в неделю")],
        [InlineKeyboardButton("Отмена", callback_data="отмена")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard) # создание клавиатуры (кнопок)
    
    await update.message.reply_text(f"Отлично! Теперь укажите, как часто вы хотите выполнять '{habit_name}':", reply_markup=reply_markup)
    return FREQUENCY


async def handle_frequency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query # получение данных и контекста о нажатой кнопке
    await query.answer()
    
    if query.data == "отмена":
        await query.edit_message_text("Создание привычки отменено.")
        return ConversationHandler.END
    
    context.user_data['frequency'] = query.data
    
    # Создаем клавиатуру с выбором времени
    keyboard = [
    [InlineKeyboardButton("00:00", callback_data="0"), InlineKeyboardButton("01:00", callback_data="1")],
    [InlineKeyboardButton("02:00", callback_data="2"), InlineKeyboardButton("03:00", callback_data="3")],
    [InlineKeyboardButton("04:00", callback_data="4"), InlineKeyboardButton("05:00", callback_data="5")],
    [InlineKeyboardButton("06:00", callback_data="6"), InlineKeyboardButton("07:00", callback_data="7")],
    [InlineKeyboardButton("08:00", callback_data="8"), InlineKeyboardButton("09:00", callback_data="9")],
    [InlineKeyboardButton("10:00", callback_data="10"), InlineKeyboardButton("11:00", callback_data="11")],
    [InlineKeyboardButton("12:00", callback_data="12"), InlineKeyboardButton("13:00", callback_data="13")],
    [InlineKeyboardButton("14:00", callback_data="14"), InlineKeyboardButton("15:00", callback_data="15")],
    [InlineKeyboardButton("16:00", callback_data="16"), InlineKeyboardButton("17:00", callback_data="17")],
    [InlineKeyboardButton("18:00", callback_data="18"), InlineKeyboardButton("19:00", callback_data="19")],
    [InlineKeyboardButton("20:00", callback_data="20"), InlineKeyboardButton("21:00", callback_data="21")],
    [InlineKeyboardButton("22:00", callback_data="22"), InlineKeyboardButton("23:00", callback_data="23")],
    [InlineKeyboardButton("Отмена", callback_data="cancel")]
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