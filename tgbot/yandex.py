from yandex_music import ClientAsync
from config import YANDEX_TOKEN, TRACKS_DIRECTORY


async def init_client():
    global client
    client = await ClientAsync(YANDEX_TOKEN).init()


async def download_song(album: int, track: int) -> tuple:
    path = TRACKS_DIRECTORY / f'{track}:{album}.mp3'
    thumb_path = TRACKS_DIRECTORY / f'{album}.jpg'
    track = (await client.tracks([f'{track}:{album}']))[0]
    if not path.exists():
        await track.download_async(path)
    if not thumb_path.exists():
        await track.download_cover_async(thumb_path)
    title = track.title
    performer =  ', '.join(map(lambda i: i['name'], track.artists[:3]))
    return path, thumb_path, title, performer


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
