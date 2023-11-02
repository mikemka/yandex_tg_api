from config import YANDEX_TOKEN, TRACKS_DIRECTORY, SYMBOLS, SYMBOLS_LEN
import mutagen
from pathlib import Path
from mutagen.easyid3 import EasyID3
from yandex_music import ClientAsync


# Initialising
async def init_client() -> None:
    global client
    client = await ClientAsync(YANDEX_TOKEN).init()


# Main requests
async def get_artist(artist_id: int, tracks_page=0, page_size=10) -> tuple:
    artist = (await client.artists(artist_ids=[artist_id]))[0]
    tracks_req = (await artist.get_tracks_async(page=tracks_page, page_size=page_size))
    tracks, pager = tracks_req.tracks, tracks_req.pager
    tracks_ids, tracks_titles_output = [], ''
    for index, track in enumerate(tracks, start=tracks_page * page_size + 1):
        tracks_ids += [(index, f'{track.id}:{track.albums[0].id}')]
        tracks_titles_output += (
            f'<code>{index}.</code> <b>{track.title}</b> – '
            f'<i>{", ".join(map(lambda i: i.name, track.artists[:3]))}</i>\n'
        )
    return (
        artist.name,
        tracks_ids,
        tracks_titles_output,
        tracks_page > 0,
        (tracks_page + 1) * page_size < pager.total,
    )


async def download_song(album: int, track_id: int) -> tuple:
    track = (await client.tracks([f'{track_id}:{album}']))[0]
    
    performer = ', '.join(map(lambda i: i['name'], track.artists[:3]))
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
                'performer': ', '.join(map(lambda i: i['name'], track['artists'][:3])),
            }
        ]
    return results


# Utils
async def generate_track_path(title: str, performer: str, track: int) -> Path:
    shorted_track_id = ''
    while track > 0:
        shorted_track_id = SYMBOLS[track % SYMBOLS_LEN] + shorted_track_id
        track //= SYMBOLS_LEN
    return TRACKS_DIRECTORY / f'{title} - {performer} :{shorted_track_id}:.mp3'
