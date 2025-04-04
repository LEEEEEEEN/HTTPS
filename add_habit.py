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

NAME, FREQUENCY, HOUR, END_CHAT = range(4)

async def cancel_conversation(update):
    await update.message.reply_text("Создание привычки отменено.")
    return ConversationHandler.END

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
    
    if query and query.data == "отмена": cancel_conversation(update)
    
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
    [InlineKeyboardButton("Отмена", callback_data="отмена")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("В какой час напомнить о привычке?", reply_markup=reply_markup)
    return HOUR

async def handle_hour(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query and query.data == "отмена": cancel_conversation(update)
    
    context.user_data['hour'] = query.data
    
    keyboard = []
    for min in range(1, 61, 4):
        row = [InlineKeyboardButton(f"{query.data}:" + f"{min - 1}".zfill(2), callback_data=f"{min - 2}"),
               InlineKeyboardButton(f"{query.data}:" + f"{min}".zfill(2), callback_data=f"{min - 1}"),
               InlineKeyboardButton(f"{query.data}:" + f"{min + 1}".zfill(2), callback_data=f"{min}"),
               InlineKeyboardButton(f"{query.data}:" + f"{min + 2}".zfill(2), callback_data=f"{min + 1}"),]
        keyboard.append(row)
        
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("В какую минуту?", reply_markup=reply_markup)
    return END_CHAT

async def handle_end_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query and query.data == "отмена": cancel_conversation(update)
    
    
    minut = query.data
    # Формируем итоговое сообщение
    habit_name = context.user_data['habit_name']
    frequency = context.user_data['frequency']
    hour = context.user_data['hour']
    
    await query.edit_message_text(
        f"Привычка '{habit_name}' успешно создана! Вы будете выполнять её {frequency} в {hour}:" + f"{minut}".zfill(2)
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Создание привычки отменено.")
    return ConversationHandler.END


def add_habit(application):
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("add_habit", start_habit_creation)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            HOUR: [CallbackQueryHandler(handle_hour)],
            FREQUENCY: [CallbackQueryHandler(handle_frequency)],
            END_CHAT: [CallbackQueryHandler(handle_end_chat)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    application.add_handler(conv_handler)