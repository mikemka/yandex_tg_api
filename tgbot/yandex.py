from aiogram.utils.markdown import quote_html
from config import YANDEX_TOKEN, TRACKS_DIRECTORY
import mutagen
from mutagen.easyid3 import EasyID3
from yandex_music import ClientAsync
from utils import generate_track_path
from simplejson import loads


# Initialising
async def init_client() -> None:
    global client
    client = await ClientAsync(YANDEX_TOKEN).init()


# Main requests
async def get_artist(artist_id: int, tracks_page=0, page_size=10) -> tuple:
    artist = (await client.artists(artist_ids=[artist_id]))[0]
    tracks_req = await artist.get_tracks_async(page=tracks_page, page_size=page_size)
    tracks, pager = tracks_req.tracks, tracks_req.pager
    tracks_ids, tracks_titles_output = [], ''
    for index, track in enumerate(tracks, start=tracks_page * page_size + 1):
        tracks_ids += [(index, f'{track.id}:{track.albums[0].id}')]
        tracks_titles_output += (
            f'<code>{index}.</code> <b>{quote_html(track.title)}</b> – '
            f'<i>{quote_html(", ".join(map(lambda i: i.name, track.artists[:3])))}</i>\n'
        )
    return (
        artist.name,
        tracks_ids,
        tracks_titles_output,
        tracks_page > 0,
        (tracks_page + 1) * page_size < pager.total,
        pager,
    )


async def get_artist_albums(artist_id: int, albums_page=0, page_size=10) -> tuple:
    artist = (await client.artists(artist_ids=[artist_id]))[0]
    albums = await artist.get_albums_async(page=albums_page, page_size=page_size)
    pager = albums.pager
    albums_ids, albums_titles_output = [], ''
    for index, album in enumerate(albums, start=albums_page * page_size + 1):
        albums_ids += [(index, album.id)]
        albums_titles_output += f'<code>{index}.</code> <b>{quote_html(album.title)}</b> – <i>[альбом]</i>\n'
    return (
        artist.name,
        albums_ids,
        albums_titles_output,
        albums_page > 0,
        (albums_page + 1) * page_size < pager.total,
        pager,
    )


async def get_album(album_id: int, tracks_page=0, page_size=10) -> tuple:
    album = await client.albums_with_tracks(album_id=album_id)
    tracks_total = album['track_count']
    tracks, volume_ids, _local_tracks_total = [], {}, 1
    for volume_id, part in enumerate(album['volumes'], start=1):
        tracks += part  # unpack discs lists to large list
        volume_ids[volume_id] = _local_tracks_total
        _local_tracks_total += len(part)
    tracks_ids, tracks_titles_output = [], ''
    for index, track in enumerate(
        tracks[tracks_page * page_size:(tracks_page + 1) * page_size],
        start=tracks_page * page_size + 1
    ):
        tracks_ids += [(index, f'{track.id}:{track.albums[0].id}')]
        if len(volume_ids) > 1:
            for volume_id in volume_ids:
                if volume_ids[volume_id] == tracks_page * page_size + index:
                    tracks_titles_output += '\n' if volume_id != 1 else ''
                    tracks_titles_output += f'<u>Диск {volume_id}</u>\n\n'
                    break
        tracks_titles_output += (
            f'<code>{index}.</code> <b>{quote_html(track.title)}</b> – '
            f'<i>{quote_html(", ".join(map(lambda i: i.name, track.artists[:3])))}</i>\n'
        )
    return (
        album.title,
        tracks_ids,
        tracks_titles_output,
        tracks_page > 0,
        (tracks_page + 1) * page_size < tracks_total,
        {
            'page': tracks_page,
            'per_page': page_size,
            'total': tracks_total,
        },
    )


async def get_playlist(playlist_id: str, tracks_page=0, page_size=10) -> tuple:
    playlist_user_id, playlist_kind = playlist_id.split(':')
    playlist = await client.users_playlists(kind=playlist_kind, user_id=playlist_user_id)
    tracks = playlist.tracks
    tracks_ids, tracks_titles_output = [], ''
    for index, _track in enumerate(
        tracks[tracks_page * page_size:(tracks_page + 1) * page_size],
        start=tracks_page * page_size + 1
    ):
        track = _track.track
        tracks_ids += [(index, f'{track.id}:{track.albums[0].id}')]
        tracks_titles_output += (
            f'<code>{index}.</code> <b>{quote_html(track.title)}</b> – '
            f'<i>{quote_html(", ".join(map(lambda i: i.name, track.artists[:3])))}</i>\n'
        )
    return (
        playlist.title,
        tracks_ids,
        tracks_titles_output,
        tracks_page > 0,
        (tracks_page + 1) * page_size < playlist.pager['total'],
        {
            'page': tracks_page,
            'per_page': page_size,
            'total': playlist.pager.total,
        },
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
    
    best_result = result.best
    output = {
        'best_type': best_result.type if best_result.type in ('album', 'artist', 'playlist', 'track') else None,
        'albums': [], 'artists': [], 'playlists': [], 'tracks': [],
    }
    
    match best_result.type:
        case 'album':
            output['albums'] = [(best_result.result.id, best_result.result.title)]
        case 'artist':
            output['artists'] = [(best_result.result.id, best_result.result.name)]
        case 'playlist':
            output['playlists'] = [(
                f'{best_result.result.owner.login}:{best_result.result.kind}',
                best_result.result.title,
            )]
        case 'track':
            track = best_result.result
            output['tracks'] = [{
                'track_id': track.id,
                'album_id': track.albums[0].id,
                'title': track.title,
                'performer': ', '.join(map(lambda i: i.name, track.artists[:3])),
            }]
    
    match search_type:
        case 'album':
            x = 1 if best_result.type == 'albums' else 0
            if result.albums is not None:
                for album in result.albums.results[x:x + 5]:
                    output['albums'] += [(album.id, album.title)]
        case 'artist':
            x = 1 if best_result.type == 'artist' else 0
            if result.artists is not None:
                for artist in result.artists.results[x:x + 5]:
                    output['artists'] += [(artist.id, artist.name)]
        case 'playlist':
            if result.playlists is not None:
                for playlist in result.playlists.results[1 if best_result.type == 'playlist' else 0:]:
                    output['playlists'] += [(
                        f'{playlist.owner.login}:{playlist.kind}',
                        playlist.title,
                    )]
        case 'track':
            x = 1 if best_result.type == 'track' else 0
            if result.tracks is not None:
                for track in result.tracks.results[x:x + 5]:
                    output['tracks'] += [{
                        'track_id': track.id,
                        'album_id': track.albums[0].id,
                        'title': track.title,
                        'performer': ', '.join(map(lambda i: i.name, track.artists[:3])),
                    }]
    return output
