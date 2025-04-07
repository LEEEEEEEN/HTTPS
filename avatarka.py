from telegram import Bot
from telegram.ext import ApplicationBuilder
bot_token = '8100915495:AAFDv6ITyBPHY7pc7qKZuyWqkc_yG4BFkPQ'
bot = Bot(token=bot_token)

with open('materials/Healthy habit Customizable Cartoon Illustrations _ Bro Style.jpeg', 'rb') as photo:
    bot.set_chat_photo(chat_id='@habits_tracker_lms_bot', photo=photo)