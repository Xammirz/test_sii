from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.web_app_info import WebAppInfo

bot = Bot('6256219480:AAHyT62NNppMEcbgf1HO4-VBVaxC2tDLl4g')
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start(message: types.message):
    markup = types.ReplyKeyboardMarkup()
    markup.add(types.KeyboardButton('Открыть web страницу', web_app=WebAppInfo(url='https://xamerzaev.github.io/DikNus/')))
    await message.answer('Добро пожаловать!', reply_markup=markup)


executor.start_polling(dp)