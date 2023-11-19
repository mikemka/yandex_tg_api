from config import STATS_DIR
from datetime import datetime
from pathlib import Path


NEW_USERS_LOG = STATS_DIR / 'users.log'

SEARCH_HISTORY_LOG = STATS_DIR / 'search_history.log'

DOWNLOADED_SONGS_LOG = STATS_DIR / 'downloaded.log'

MAILING_LOG = STATS_DIR / 'mailing.log'


def escape_newline(s: str) -> str:
    return str(s).replace('\n', '\\n').replace('\t', '\\t')


def write_log(filepath: Path, log_info: tuple | list):
    if not filepath.exists():
        with open(filepath, 'x'):
            pass
    with open(filepath, 'a') as log_file:
        log_file.write(
            f'{datetime.now().strftime("%Y/%m/%d %H:%M:%S")};'
            f'{";".join(map(escape_newline, log_info))}\n'
        )


def new_user_log(user_id: int):
    write_log(NEW_USERS_LOG, user_id)


def new_search_log(user_id: int, search_request: str, search_type: str):
    write_log(SEARCH_HISTORY_LOG, (user_id, search_request, search_type))


def new_download_log(user_id: int, song_id: str):
    write_log(DOWNLOADED_SONGS_LOG, (user_id, song_id))


def new_mailing_log(admin_id: int, users_list: list | tuple):
    write_log(MAILING_LOG, (admin_id, str(list(users_list)).replace(' ', '')))
