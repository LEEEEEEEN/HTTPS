import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, ContextTypes
from data import get_user_habits

API_KEY = "4f884c887bcb893bc838b219878a7db2"
CITIES = [
    "Москва",
    "Санкт-Петербург",
    "Казань",
    "Тверь",
    "Можайск",
    "Ижевск",
    "Новосибирск",
    "Владивосток",
    "Краснодар"
]

weatherlock = [
    "дождь", "снег", "метель", "пасмурно", "гроза", "ливень", "шторм", "туман"
]

keyword = [
    "на улице", "бегать", "гулять", "кататься", "плавать"
]

habitss = [
    "прыгать", "тренироваться", "спорт"
]

whereah = [
    "в зале", "дома", "в помещении"
]

CITY = 0


async def weather_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(city, callback_data=city)] for city in CITIES
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Выберите город для получения погоды:",
        reply_markup=reply_markup
    )
    return CITY


async def get_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    city = query.data

    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city,
        'appid': API_KEY,
        'units': 'metric',
        'lang': 'ru'
    }

    try:
        response = requests.get(base_url, params=params).json()
        if response.get("cod") != 200:
            await query.edit_message_text(f"Не удалось получить погоду для {city}. Попробуйте позже.")
            return ConversationHandler.END

        weather_desc = response["weather"][0]["description"]
        temp = response["main"]["temp"]
        feels_like = response["main"]["feels_like"]
        message = (
            f"Погода в {city}:\n"
            f"Описание: {weather_desc.capitalize()}\n"
            f"Температура: {temp}°C\n"
            f"Ощущается как: {feels_like}°C"
        )
        await query.edit_message_text(message)

        is_bad_weather = any(keyword in weather_desc.lower() for keyword in weatherlock)
        if is_bad_weather:
            user_id = update.effective_user.id
            habits = await get_user_habits(user_id)
            outdoor_habits = [
                habit["name"] for habit in habits
                if (
                        any(keyword in habit["name"].lower() for keyword in keyword)
                        or
                        (
                                any(keyword in habit["name"].lower() for keyword in habitss)
                                and not any(indoor in habit["name"].lower() for indoor in whereah)
                        )
                )
            ]
            if outdoor_habits:
                habits_list = ", ".join(outdoor_habits)
                await query.message.reply_text(
                    f"Не советую сегодня выполнять эти привычки из-за погоды:\n{habits_list}."
                )
    except Exception as e:
        await query.edit_message_text(f"Ошибка при получении погоды: {e}")
    return ConversationHandler.END


def weather_handler(application: Application):
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("weather", weather_start)],
        states={
            CITY: [CallbackQueryHandler(get_weather)]
        },
        fallbacks=[],
        per_message=False
    )
    application.add_handler(conv_handler)
