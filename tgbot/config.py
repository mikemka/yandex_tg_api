import dotenv
import os
import pathlib


BASE_DIR = pathlib.Path(__file__).resolve().parent.parent

DOTENV_PATH = BASE_DIR / '.env'

if DOTENV_PATH.exists():
    dotenv.load_dotenv(DOTENV_PATH)

API_TOKEN = os.getenv('API_TOKEN')

YANDEX_TOKEN = os.getenv('YANDEX_TOKEN')

DATABASE = BASE_DIR / 'database.db'

TRACKS_DIRECTORY = BASE_DIR / 'tracks'

if not TRACKS_DIRECTORY.exists():
    os.mkdir(TRACKS_DIRECTORY)
