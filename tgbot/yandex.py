from yandex_music import ClientAsync
from config import YANDEX_TOKEN, TRACKS_DIRECTORY, SYMBOLS, SYMBOLS_LEN
import mutagen
from mutagen.easyid3 import EasyID3


async def init_client():
    global client
    client = await ClientAsync(YANDEX_TOKEN).init()


async def download_song(album: int, track_id: int) -> tuple:
    track = (await client.tracks([f'{track_id}:{album}']))[0]
    
    performer = await generate_performer_string(track.artists)
    path = await generate_track_path(
        title=track.title,
        performer=performer,
        track=int(track_id),
    )
    
    thumb_path = TRACKS_DIRECTORY / f'{album}.jpg'
    
    if not path.exists():
        await track.download_async(path)
    if not thumb_path.exists():
        await track.download_cover_async(thumb_path)
    
    try:
        meta = EasyID3(path)
    except mutagen.id3.ID3NoHeaderError:
        meta = mutagen.File(path, easy=True)
        meta.add_tags()
    meta['title'] = track.title
    meta['artist'] = performer
    meta.save(path, v1=2)

    return path, thumb_path, track.title, performer


async def generate_track_path(title: str, performer: str, track: int):
    shorted_track_id = ''
    while track > 0:
        shorted_track_id = SYMBOLS[track % SYMBOLS_LEN] + shorted_track_id
        track //= SYMBOLS_LEN
    return TRACKS_DIRECTORY / f'{title} - {performer} :{shorted_track_id}:.mp3'


async def generate_performer_string(artists: list):
    return ', '.join(map(lambda i: i['name'], artists[:3]))


async def search(text: str) -> list:
    results, tracks = [], (await client.search(text=text))['tracks']
    if tracks is None:
        return None
    for track in tracks['results'][:6]:
        results += [
            {
                'track_id': track['id'],
                'album_id': track['albums'][0]['id'],
                'title': track['title'],
                'performer': await generate_performer_string(track['artists']),
            }
        ]
    return results
