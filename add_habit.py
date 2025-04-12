from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, CallbackQueryHandler, filters, \
    ContextTypes
from data import save_habit

NAME, FREQUENCY, HOUR, MINUTE, END_CHAT, WEEK = range(6)

user_habits = {}
hour_keyboard = [
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
        [InlineKeyboardButton("22:00", callback_data="22"), InlineKeyboardButton("23:00", callback_data="23")]
    ]
translate_week = {
    "mon": "каждый понедельник",
    "tue": "каждый вторник",
    "wed": "каждую среду",
    "thu": "каждый четверг",
    "fri": "каждую пятницу",
    "sat": "каждую субботу",
    "sun": "каждое воскресенье"
}


async def start_habit_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Начнем создание привычки! Как назовем её?")
    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    habit_name = update.message.text
    context.user_data['habit_name'] = habit_name
    await update.message.reply_text(f"Отлично! Как часто вы хотите выполнять '{habit_name}'?")

    keyboard = [
        [InlineKeyboardButton("Ежедневно", callback_data="ежедневно")],
        [InlineKeyboardButton("Раз в неделю", callback_data="неделя")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Выберите частоту:", reply_markup=reply_markup)
    return FREQUENCY


async def handle_frequency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "неделя":
        keyboard = [
            [InlineKeyboardButton("ПН", callback_data="mon"), 
             InlineKeyboardButton("ВТ", callback_data="tue"),
             InlineKeyboardButton("СР", callback_data="wed"),
             InlineKeyboardButton("ЧТ", callback_data="thu"),
             InlineKeyboardButton("ПТ", callback_data="fri"),
             InlineKeyboardButton("СБ", callback_data="sat"),
             InlineKeyboardButton("ВС", callback_data="sun"),]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Какой день недели?", reply_markup=reply_markup)
        return WEEK
    else:
        context.user_data['frequency'] = query.data
        reply_markup = InlineKeyboardMarkup(hour_keyboard)
        await query.edit_message_text("В какой час напомнить о привычке?", reply_markup=reply_markup)
    return HOUR

async def week_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    context.user_data['frequency'] = query.data
    reply_markup = InlineKeyboardMarkup(hour_keyboard)
    await query.edit_message_text("В какой час напомнить о привычке?", reply_markup=reply_markup)
    return HOUR
    

async def handle_hour(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['hour'] = query.data
    await query.edit_message_text("В какую минуту часа?")
    
    return MINUTE


async def handle_minute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    minute = update.message.text

    if not minute.isdigit():
        await update.message.reply_text(f"Отправь просто число от 0 до 59")
        return MINUTE
    else:
        if int(minute) < 0 or int(minute) > 59:
            return MINUTE

    habit_name = context.user_data['habit_name']
    frequency = context.user_data['frequency']
    hour = context.user_data['hour']

    # Сохраняем привычку
    user_id = update.effective_user.id
    
    habit = {
        "name": habit_name,
        "frequency": frequency,
        "time": f"{hour}:{minute.zfill(2)}"
    }

    if user_id not in user_habits:
        user_habits[user_id] = []

    await save_habit(user_id, habit)
    
    user_habits[user_id].append(habit)

    await update.message.reply_text(f"Привычка '{habit_name}' успешно создана! Вы будете выполнять её {translate_week[frequency]} в {hour}:{minute.zfill(2)}.")
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Создание привычки отменено.")
    return ConversationHandler.END


def add_habit(application):
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("add_habit", start_habit_creation)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            FREQUENCY: [CallbackQueryHandler(handle_frequency)],
            HOUR: [CallbackQueryHandler(handle_hour)],
            WEEK: [CallbackQueryHandler(week_handler)],
            MINUTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_minute)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

