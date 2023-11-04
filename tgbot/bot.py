import logging
from aiogram import executor
from asyncio import ensure_future
from dispather import dp
from config import DATABASE
from database import create_tables
import handlers
from yandex import init_client


logging.basicConfig(level=logging.INFO)

ensure_future(init_client())

if not DATABASE.exists():
    create_tables()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
