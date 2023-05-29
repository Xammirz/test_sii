import os
import threading
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.web_app_info import WebAppInfo
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv
from google_sheets import main

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_CHAT_IDS = os.getenv("ALLOWED_CHAT_IDS")

URL = 'https://xamerzaev.github.io/DikNus/'
START_TEXT = 'Добро пожаловать!'
START_BUTTON = 'Приступить'
DATA_DOWNLOAD_BUTTON = 'Запустить загрузку данных'
LOADING_STARTED_TEXT = 'Начата загрузка данных...'
LOADING_COMPLETED_TEXT = 'Загрузка данных завершена.'

if not TELEGRAM_BOT_TOKEN or not ALLOWED_CHAT_IDS:
    raise ValueError("Please provide TELEGRAM_BOT_TOKEN and ALLOWED_CHAT_IDS in the .env file.")

allowed_chats = ALLOWED_CHAT_IDS.split(",")

bot = Bot(TELEGRAM_BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if str(message.chat.id) not in allowed_chats:
        await message.answer("Извините, вы не можете использовать этого бота.")
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton(START_BUTTON, web_app=WebAppInfo(url=URL)))
    
    if str(message.chat.id) == allowed_chats[0]:
        markup.add(types.KeyboardButton(DATA_DOWNLOAD_BUTTON))
    
    await message.answer(START_TEXT, reply_markup=markup)


@dp.callback_query_handler(lambda query: query.data == 'execute_main')
async def execute_main_callback(query: types.CallbackQuery):
    await bot.answer_callback_query(query.id)
    await bot.send_message(query.from_user.id, LOADING_STARTED_TEXT)
    threading.Thread(target=main).start()
    await bot.send_message(query.from_user.id, LOADING_COMPLETED_TEXT)


@dp.message_handler(Command('cancel'), state='*')
@dp.message_handler(lambda message: message.text == DATA_DOWNLOAD_BUTTON, state='*')
async def execute_main_message(message: types.Message, state: FSMContext):
    await message.answer(LOADING_STARTED_TEXT)
    threading.Thread(target=main).start()
    await message.answer(LOADING_COMPLETED_TEXT)
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
