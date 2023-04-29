import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.web_app_info import WebAppInfo

load_dotenv()

token= os.getenv("TELEGRAM_BOT_TOKEN")

bot = Bot(token)
dp = Dispatcher(bot)

# Импортируем функции для работы с json файлом
import json

def get_dealer_checklist(city_id: str, dealer_name: str):
    # Открываем json файл с данными
    with open('data.json', 'r') as f:
        data = json.load(f)
    
    # Ищем нужного дилера в выбранном городе
    dealers = data['dealers'][city_id]
    dealer = next((d for d in dealers if d['name'] == dealer_name), None)
    if not dealer:
        return None
    
    # Возвращаем чек-лист для дилера
    return dealer.get('checklist', None)

@dp.message_handler(commands=['start'])
async def start(message: types.message):
    markup = types.ReplyKeyboardMarkup()
    markup.add(types.KeyboardButton('Открыть web страницу', web_app=WebAppInfo(url='https://xamerzaev.github.io/DikNus/')))
    await message.answer('Добро пожаловать!', reply_markup=markup)

@dp.message_handler(commands=['checklist'])
async def checklist(message: types.message):
    # Получаем id города и название дилера из сообщения пользователя
    city_id, dealer_name = message.text.split()[1:]
    
    # Получаем чек-лист для дилера
    checklist = get_dealer_checklist(city_id, dealer_name)
    
    if checklist:
        # Если чек-лист найден, отправляем его пользователю
        await message.answer('\n'.join(checklist))
    else:
        # Если дилер не найден, отправляем сообщение об ошибке
        await message.answer('Дилер не найден')

executor.start_polling(dp)
