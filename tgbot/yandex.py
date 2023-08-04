from yandex_music import Client
from config import YANDEX_TOKEN, TRACKS_DIRECTORY


client = Client(YANDEX_TOKEN).init()


def download_song(album: int, track: int) -> tuple:
    path = TRACKS_DIRECTORY / f'{track}:{album}.mp3'
    thumb_path = TRACKS_DIRECTORY / f'{album}.jpg'
    track = client.tracks([f'{track}:{album}'])[0]
    if not path.exists():
        track.download(path)
    if not thumb_path.exists():
        track.download_cover(thumb_path)
    title = track.title
    performer =  ', '.join(map(lambda i: i['name'], track.artists[:3]))
    return path, thumb_path, title, performer


def search(text: str) -> list:
    results = []
    tracks = client.search(text=text)['tracks']
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
