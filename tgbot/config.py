from ast import literal_eval
from dotenv import load_dotenv
from os import getenv, mkdir
from pathlib import Path
from string import digits, ascii_letters, punctuation


BASE_DIR = Path(__file__).resolve().parent.parent

DOTENV_PATH = BASE_DIR / '.env'

PICKLE_PATH = BASE_DIR / 'storage.pickle'

if DOTENV_PATH.exists():
    load_dotenv(DOTENV_PATH)

ADMIN_IDS = literal_eval(getenv('ADMIN_IDS', '[688003991]'))

API_TOKEN = getenv('API_TOKEN')

DATABASE = BASE_DIR / 'database.db'

STORAGE_PATH = BASE_DIR / 'storage.json'

YANDEX_TOKEN = getenv('YANDEX_TOKEN')

TRACKS_DIRECTORY = BASE_DIR / 'tracks'

SYMBOLS = digits + ascii_letters + punctuation

SYMBOLS_LEN = len(SYMBOLS)

ENG_TO_RUS_TYPE = {'album': 'альбом', 'artist': 'исполнитель', 'playlist': 'плейлист', 'track': 'трек'}

SEARCH_TYPES = ('track', 'artist', 'album', 'playlist')

if not TRACKS_DIRECTORY.exists():
    mkdir(TRACKS_DIRECTORY)
