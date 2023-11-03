from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.files import PickleStorage
from config import API_TOKEN, PICKLE_PATH


bot = Bot(token=API_TOKEN, parse_mode='HTML')

dp = Dispatcher(bot, storage=PickleStorage(PICKLE_PATH))
