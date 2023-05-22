from dotenv import load_dotenv
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.web_app_info import WebAppInfo
from google_sheets import main

load_dotenv()

token = os.getenv("TELEGRAM_BOT_TOKEN")
allowed_chats = os.getenv("ALLOWED_CHAT_IDS").split(",")

bot = Bot(token)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if str(message.chat.id) not in allowed_chats:
        await message.answer("Извините, вы не можете использовать этого бота.")
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton('Приступить', web_app=WebAppInfo(url='https://xamerzaev.github.io/DikNus/')))
    
    if str(message.chat.id) == allowed_chats[0]:
        markup.add(types.KeyboardButton('Запустить загрузку данных'))
    
    await message.answer('Добро пожаловать!', reply_markup=markup)

@dp.message_handler(lambda message: message.text == 'Запустить загрузку данных')
async def execute_main(message: types.Message):
    await message.answer("Начата загрузка данных...")
    main()
    await message.answer("Загрузка данных завершена.")

if __name__ == '__main__':
    executor.start_polling(dp)
