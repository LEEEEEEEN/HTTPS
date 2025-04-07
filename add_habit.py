from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, CallbackQueryHandler, filters, \
    ContextTypes

NAME, FREQUENCY, HOUR, MINUTE, END_CHAT = range(5)

user_habits = {}


async def cancel_conversation(update: Update):
    await update.message.reply_text("Создание привычки отменено.")
    return ConversationHandler.END


async def start_habit_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Начнем создание привычки! Как назовем её?")
    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    habit_name = update.message.text
    context.user_data['habit_name'] = habit_name
    await update.message.reply_text(f"Отлично! Как часто вы хотите выполнять '{habit_name}'?")

    keyboard = [
        [InlineKeyboardButton("Ежедневно", callback_data="ежедневно")],
        [InlineKeyboardButton("Раз в неделю", callback_data="раз в неделю")],
        [InlineKeyboardButton("Отмена", callback_data="отмена")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Выберите частоту:", reply_markup=reply_markup)
    return FREQUENCY


async def handle_frequency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data['frequency'] = query.data

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
        [InlineKeyboardButton("22:00", callback_data="22"), InlineKeyboardButton("23:00", callback_data="23")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text("В какой час напомнить о привычке?", reply_markup=reply_markup)
    return HOUR



async def handle_hour(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query and query.data == "отмена":
        return cancel_conversation(update)

    context.user_data['hour'] = query.data

    keyboard = []
    for min in range(0, 60, 5):
        row = [InlineKeyboardButton(f"{query.data}:{str(min).zfill(2)}", callback_data=f"{min}")]
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text("Выберите минуту напоминания:", reply_markup=reply_markup)
    return MINUTE


async def handle_minute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query and query.data == "отмена":
        return cancel_conversation(update)

    minute = query.data
    habit_name = context.user_data['habit_name']
    frequency = context.user_data['frequency']
    hour = context.user_data['hour']

    # Сохраняем привычку
    user_id = query.from_user.id
    habit = {
        "name": habit_name,
        "frequency": frequency,
        "time": f"{hour}:{minute.zfill(2)}"
    }

    if user_id not in user_habits:
        user_habits[user_id] = []

    user_habits[user_id].append(habit)

    await query.edit_message_text(
        f"Привычка '{habit_name}' успешно создана! Вы будете выполнять её {frequency} в {hour}:{minute.zfill(2)}.")
    return ConversationHandler.END


async def show_habits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    habits = user_habits.get(user_id, [])

    if not habits:
        await update.message.reply_text("У вас пока нет привычек.")
        return

    message = "Ваши привычки:\n\n"
    for i, h in enumerate(habits, start=1):
        message += f"{i}. {h['name']} — {h['frequency']} в {h['time']}\n"

    await update.message.reply_text(message)


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
            MINUTE: [CallbackQueryHandler(handle_minute)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

