from config import YANDEX_TOKEN, TRACKS_DIRECTORY
import mutagen
from mutagen.easyid3 import EasyID3
from yandex_music import ClientAsync
from utils import generate_track_path


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
        pager,
    )


async def download_song(album: int, track_id: int) -> tuple:
    track = (await client.tracks([f'{track_id}:{album}']))[0]
    
    performer = ', '.join(map(lambda i: i['name'], track.artists[:3]))
    path = generate_track_path(
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


async def search(text: str, search_type='track') -> dict | None:
    """
    Returns dict `output`
    
    albums, artists, playlists: [(id, title|name), ]
    track: [{'track_id', 'album_id', 'title', 'performer'}, ]
    """
    
    assert search_type in ('album', 'artist', 'playlist', 'track')
    
    result = await client.search(type_='all', text=text)
    if result['best'] is None:
        return None
    
    best_type = result['best']['type']
    output = {
        'best_type': best_type if best_type in ('album', 'artist', 'playlist', 'track') else None,
        'albums': [], 'artists': [], 'playlists': [], 'tracks': [],
    }
    
    match result['best']['type']:
        case 'album':
            output['albums'] = [(result['best']['result']['id'], result['best']['result']['title'])]
        case 'artist':
            output['artists'] = [(result['best']['result']['id'], result['best']['result']['name'])]
        case 'playlist':
            output['playlists'] = [(result['best']['result']['uid'], result['best']['result']['title'])]
        case 'track':
            track = result['best']['result']
            output['tracks'] = [{
                'track_id': track['id'],
                'album_id': track['albums'][0]['id'],
                'title': track['title'],
                'performer': ', '.join(map(lambda i: i['name'], track['artists'][:3])),
            }]
    
    match search_type:
        case 'album':
            x = 1 if best_type == 'albums' else 0
            for album in result['albums']['results'][x:x + 5]:
                output['albums'] += [(album['id'], album['title'])]
        case 'artist':
            x = 1 if best_type == 'artist' else 0
            for artist in result['artists']['results'][x:x + 5]:
                output['artists'] += [(artist['id'], artist['name'])]
        case 'playlist':
            for playlist in result['playlists']['results'][1 if best_type == 'playlist' else 0:]:
                output['playlists'] += [(playlist['uid'], playlist['title'])]
        case 'track':
            x = 1 if best_type == 'track' else 0
            for track in result['tracks']['results'][x:x + 5]:
                output['tracks'] += [{
                    'track_id': track['id'],
                    'album_id': track['albums'][0]['id'],
                    'title': track['title'],
                    'performer': ', '.join(map(lambda i: i['name'], track['artists'][:3])),
                }]
    return output
