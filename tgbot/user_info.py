from simplejson import dump, load
from config import STORAGE_PATH
from time import time as current_time
from utils import short_id


def get_search_type(user_id: int | str) -> int:
    if type(user_id) == int:
        user_id = str(user_id)

    if not STORAGE_PATH.exists():
        with open(STORAGE_PATH, 'w') as json_storage:
            dump({"search_type": {}, "search_requests": {}}, json_storage)
        return 0
    
    with open(STORAGE_PATH, 'r') as json_storage:
        storage = load(json_storage)
    
    if user_id in storage['search_type']:
        return storage['search_type'][user_id]
    
    storage['search_type'][user_id] = 0
    with open(STORAGE_PATH, 'w') as json_storage:
        dump(storage, json_storage)
    return 0


def next_search_type(user_id: int | str) -> int:
    if type(user_id) == int:
        user_id = str(user_id)

    if not STORAGE_PATH.exists():
        with open(STORAGE_PATH, 'w') as json_storage:
            dump({"search_type": {user_id: 1}, "search_requests": {}}, json_storage)
        return 1

    with open(STORAGE_PATH, 'r') as json_storage:
        storage = load(json_storage)
    
    storage['search_type'][user_id] = (storage['search_type'].setdefault(user_id, 0) + 1) % 4
    
    with open(STORAGE_PATH, 'w') as json_storage:
        dump(storage, json_storage)
    return storage['search_type'][user_id]


def save_search_request(text: str) -> str:
    search_id = short_id(int(current_time() * 2_100_000))
    
    if not STORAGE_PATH.exists():
        with open(STORAGE_PATH, 'w') as json_storage:
            dump({"search_type": {}, "search_requests": {search_id: text}}, json_storage)
        return search_id

    with open(STORAGE_PATH, 'r') as json_storage:
        storage = load(json_storage)
    
    storage['search_requests'][search_id] = text
    
    with open(STORAGE_PATH, 'w') as json_storage:
        dump(storage, json_storage)
    
    return search_id


def get_search_request(_id: str) -> str | None:
    if not STORAGE_PATH.exists():
        with open(STORAGE_PATH, 'w') as json_storage:
            dump({"search_type": {}, "search_requests": {}}, json_storage)
        return None

    with open(STORAGE_PATH, 'r') as json_storage:
        storage = load(json_storage)

    return storage['search_requests'].get(_id, None)
