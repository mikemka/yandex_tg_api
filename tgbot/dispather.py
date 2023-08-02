from aiogram import Bot, Dispatcher
from config import API_TOKEN


bot = Bot(token=API_TOKEN, parse_mode='HTML')
dp = Dispatcher(bot)
