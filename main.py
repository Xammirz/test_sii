from dotenv import load_dotenv
import os

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.web_app_info import WebAppInfo

load_dotenv()

token = os.getenv("TELEGRAM_BOT_TOKEN")

bot = Bot(token)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start(message: types.message):
    allowed_chats = os.getenv("ALLOWED_CHAT_IDS").split(",")
    if str(message.chat.id) not in allowed_chats:
        await message.answer("Извините, вы не можете использовать этого бота.")
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton('Приступить', web_app=WebAppInfo(url='https://xamerzaev.github.io/DikNus/')))
    await message.answer('Добро пожаловать!', reply_markup=markup)


executor.start_polling(dp)
