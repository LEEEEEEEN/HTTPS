import asyncio
import schedule
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, CallbackQueryHandler, filters, \
    ContextTypes

NAME, FREQUENCY, HOUR, MINUTE, END_CHAT = range(5)
user_habits = {}


# Функция для отправки напоминания
async def send_reminder(user_id, habit_name, time):
    application = await ApplicationBuilder().token("YOUR_BOT_TOKEN").build()
    await application.bot.send_message(user_id, f"Пора выполнить привычку: {habit_name} в {time}!")


# Функция для проверки привычек каждую минуту
def check_habits(application):
    async def check_time():
        while True:
            now = datetime.datetime.now().strftime("%H:%M")
            for user_id, habits in user_habits.items():
                for habit in habits:
                    if habit['time'] == now:
                        await send_reminder(user_id, habit['name'], habit['time'])
            await asyncio.sleep(60)
    asyncio.create_task(check_time())  # Запуск проверки в фоновом режиме


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
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Выберите частоту:", reply_markup=reply_markup)
    return FREQUENCY


async def handle_frequency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data['frequency'] = query.data
    keyboard = [
        [InlineKeyboardButton(f"{i}:00", callback_data=str(i)) for i in range(24)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text("В какой час напомнить о привычке?", reply_markup=reply_markup)
    return HOUR


async def handle_hour(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data['hour'] = query.data
    keyboard = [
        [InlineKeyboardButton(f"{query.data}:{str(min).zfill(2)}", callback_data=str(min)) for min in range(0, 60, 5)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text("Выберите минуту напоминания:", reply_markup=reply_markup)
    return MINUTE


async def handle_minute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    minute = query.data
    habit_name = context.user_data['habit_name']
    frequency = context.user_data['frequency']
    hour = context.user_data['hour']

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
        f"Привычка '{habit_name}' успешно создана! Вы будете выполнять её {frequency} в {hour}:{minute.zfill(2)}."
    )

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
