from ast import literal_eval
from dotenv import load_dotenv
from os import getenv, mkdir
from pathlib import Path
from string import digits, ascii_letters, punctuation


BASE_DIR = Path(__file__).resolve().parent.parent

DOTENV_PATH = BASE_DIR / '.env'

if DOTENV_PATH.exists():
    load_dotenv(DOTENV_PATH)

ADMIN_IDS = literal_eval(getenv('ADMIN_IDS', '[688003991]'))

API_TOKEN = getenv('API_TOKEN')

DATABASE = BASE_DIR / 'database.db'

YANDEX_TOKEN = getenv('YANDEX_TOKEN')

TRACKS_DIRECTORY = BASE_DIR / 'tracks'

SYMBOLS = digits + ascii_letters + punctuation

SYMBOLS_LEN = len(SYMBOLS)

if not TRACKS_DIRECTORY.exists():
    mkdir(TRACKS_DIRECTORY)
