from telegram import Update, InputFile
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from data import get_user_habits, del_user_habit, get_habit_stats

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import seaborn as sns
import numpy as np

from datetime import datetime
import calendar
from io import BytesIO

from del_habit import create_list_habits, translate_week, force_cancel
from data import get_habit_stats

MONTH_TRANSLATE = {
    'January': 'Январь',
    'February': 'Февраль',
    'March': 'Март',
    'April': 'Апрель',
    'May': 'Май',
    'June': 'Июнь',
    'July': 'Июль',
    'August': 'Август',
    'September': 'Сентябрь',
    'October': 'Октябрь',
    'November': 'Ноябрь',
    'December': 'Декабрь'
}


STATS = 0

async def stats_habit_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    habits = await get_user_habits(user_id)
    if not habits:
        await update.message.reply_text("У вас пока нет привычек для просмотра.")
        return ConversationHandler.END
    message = "По какой привычке посмотреть статистику? (отправьте номер привычки из списка)\n\n"
    message = create_list_habits(message, habits)
    await update.message.reply_text(message)
    return STATS

async def stats_hand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    habit = ""
    habits = await get_user_habits(user_id)
    if update.message.text.isdigit():
        index = int(update.message.text)
        if 0 < index <= len(habits):
            selected_habit = habits[index - 1]
            habit_name = selected_habit["name"]
            image_buffer = await render_habit_stats(user_id, habit_name)
            if image_buffer:
                await update.message.reply_photo(
                    photo=InputFile(image_buffer, filename=f"{habit_name}_stats.png"),
                    caption=f"Статистика привычки '{habit_name}'")
            else:
                await update.message.reply_text(f"Нет данных для построения графика по привычке '{habit_name}'")
                
            return ConversationHandler.END
    
    await update.message.reply_text(f"Нет там такого номера...\nОтправь цифру от 1 до {len(habits)}")
    return STATS

def get_week_and_day(date: datetime):
    year = date.year
    month = date.month
    day = date.day
    cal = calendar.monthcalendar(year, month)
    for week_index, week in enumerate(cal):
        if day in week:
            day_index = week.index(day)
            return week_index, day_index
    return None, None

async def render_habit_stats(user_id, habit_name):
    try:
        dates, success_rates = await get_habit_stats(user_id, habit_name)
        if not dates:
            return None

        date_objects = [datetime.strptime(date, "%Y-%m-%d") for date in dates]
        min_date = min(date_objects)
        year, month = min_date.year, min_date.month

        _, days_in_month = calendar.monthrange(year, month)
        cal_matrix = np.full((6, 7), '', dtype=object)
        color_matrix = np.zeros((6, 7)) 

        for date, rate in zip(date_objects, success_rates):
            week_idx, day_idx = get_week_and_day(date)
            if week_idx is not None and day_idx is not None:
                cal_matrix[week_idx][day_idx] = str(date.day)
                color_matrix[week_idx][day_idx] = 1 if rate > 0 else 0

        cal = calendar.monthcalendar(year, month)
        for week_idx, week in enumerate(cal):
            for day_idx, day in enumerate(week):
                if day != 0: 
                    if cal_matrix[week_idx][day_idx] == '':
                        cal_matrix[week_idx][day_idx] = str(day)

        cmap = ListedColormap(['lightgray', 'lightgreen'])

        fig, ax = plt.subplots(figsize=(10, 4))
        sns.heatmap(
            color_matrix,
            annot=cal_matrix,
            fmt='',
            cmap=cmap,
            cbar=False,
            square=True,
            linewidths=0.5,
            linecolor="white",
            xticklabels=["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
            yticklabels=[],
            annot_kws={"size": 10},
            ax=ax
        )

        month_en = calendar.month_name[month]
        month_ru = MONTH_TRANSLATE.get(month_en, month_en)
        ax.set_title(f"Статистика привычки '{habit_name}'  {month_ru} {year}", fontsize=12)
        ax.set_xlabel("День недели")

        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        plt.close(fig)
        buf.seek(0)
        return buf

    except Exception as e:
        print(f"Ошибка при генерации графика: {e}")
        return None

def stats_habit_handler(application):
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("stats", stats_habit_start)],
        states={
            STATS: [MessageHandler(filters.TEXT & ~filters.COMMAND, stats_hand)]
        },
        fallbacks=[MessageHandler(filters.COMMAND, force_cancel)]
    )
    application.add_handler(conv_handler)