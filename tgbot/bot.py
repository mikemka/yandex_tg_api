import logging
from aiogram import executor
from dispather import dp
from message_handlers import *
from config import DATABASE
from database import create_tables


logging.basicConfig(level=logging.INFO)

if not DATABASE.exists():
    create_tables()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
