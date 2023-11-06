from pathlib import Path
from config import TRACKS_DIRECTORY, SYMBOLS, SYMBOLS_LEN


def generate_track_path(title: str, performer: str, track: int) -> Path:
    return TRACKS_DIRECTORY / f'{title} - {performer} :{short_id(track)}:.mp3'


def short_id(_id: int) -> str:
    shorted_track_id = ''
    while _id > 0:
        shorted_track_id = SYMBOLS[_id % SYMBOLS_LEN] + shorted_track_id
        _id //= SYMBOLS_LEN
    return shorted_track_id
