from aiogram import types
from aiogram.utils.markdown import quote_html
from aiogram.dispatcher.filters import Text
from dispather import dp
from keyboards import (
    generate_artist_keyboard,
    generate_album_keyboard,
    generate_playlist_keyboard,
    generate_artist_by_album_keyboard,
)
from yandex import (
    download_song,
    get_artist,
    get_album,
    get_playlist,
    get_artist_albums,
)
from yandex_music.exceptions import BadRequestError
from os import remove
from stats_logs import new_download_log


@dp.callback_query_handler(Text(startswith="!track!"))
async def callback_track_chosen(callback: types.CallbackQuery):
    track_album, track_id = callback.data[7:].split(':')[::-1]
    try:
        result = await download_song(track_album, track_id)
    except BadRequestError:
        return await callback.bot.send_message(
            chat_id=callback.from_user.id,
            text='❌ Возможно, песня была перемещена или удалена.',
        )
    
    await callback.bot.send_chat_action(
        chat_id=callback.from_user.id,
        action='upload_document',
    )

    path, thumb_path, title, performer = result
    await callback.bot.send_audio(
        callback.from_user.id,
        audio=open(path, 'rb'),
        caption='Скачано в <a href="https://t.me/yandexMusicDownload_bot">Yandex Music Bot</a>',
        performer=performer,
        title=title,
        thumb=open(thumb_path, 'rb'),
    )
    await callback.answer()
    remove(path=path)
    remove(path=thumb_path)
    new_download_log(callback.from_user.id, ':'.join((track_album, track_id)))


@dp.callback_query_handler(Text(startswith="!artist!"))
async def callback_artist_chosen(callback: types.CallbackQuery):
    artist_id = callback.data[8:][:callback.data[8:].find('!')]
    search_id = callback.data[8:][callback.data[8:].find('!') + 1:]
    try:
        (
            artist_name,
            tracks_results,
            tracks_titles_output,
            left_btn,
            right_btn,
            pager,
        ) = await get_artist(artist_id)
    except Exception:
        return await callback.answer(text='❌ Исполнитель не найден.')
    await callback.message.edit_text(
        text=(
            f'<b>🎧 {quote_html(artist_name)}</b> '
            f'({min(((pager["page"] + 1) * pager["per_page"], pager["total"]))} из {pager["total"]})\n\n'
            f'{tracks_titles_output}'
        ),
        reply_markup=generate_artist_keyboard(tracks_results, artist_id, left_btn, right_btn, search_id),
    )


@dp.callback_query_handler(Text(startswith="!art_album!"))
async def callback_artist_album(callback: types.CallbackQuery):
    artist_id = callback.data[11:][:callback.data[11:].find('!')]
    search_id = callback.data[11:][callback.data[11:].find('!') + 1:]
    (
        artist_name,
        albums_results,
        albums_titles_output,
        left_btn,
        right_btn,
        pager,
    ) = await get_artist_albums(artist_id)
    await callback.message.edit_text(
        text=(
            f'<b>🎧 {quote_html(artist_name)}</b> '
            f'({min(((pager["page"] + 1) * pager["per_page"], pager["total"]))} из {pager["total"]})\n\n'
            f'{albums_titles_output}'
        ),
        reply_markup=generate_artist_by_album_keyboard(
            albums_results,
            artist_id,
            left_btn,
            right_btn,
            search_id,
        ),
    )


@dp.callback_query_handler(Text(startswith='#'))
async def callback_artist_album(callback: types.CallbackQuery):
    page_id = int(callback.data[1:][:callback.data.find('~') - 1])
    artist_id = int(callback.data[callback.data.find('~') + 1:callback.data.find('!')])
    search_id = callback.data[callback.data.rfind('!') + 1:]
    (
        artist_name,
        albums_results,
        albums_titles_output,
        left_btn,
        right_btn,
        pager,
    ) = await get_artist_albums(artist_id, albums_page=page_id)
    await callback.message.edit_text(
        text=(
            f'<b>🎧 {quote_html(artist_name)}</b> '
            f'({min(((pager["page"] + 1) * pager["per_page"], pager["total"]))} из {pager["total"]})\n\n'
            f'{albums_titles_output}'
        ),
        reply_markup=generate_artist_by_album_keyboard(
            albums_results,
            artist_id,
            left_btn,
            right_btn,
            search_id,
        ),
    )


@dp.callback_query_handler(Text(startswith="!album!"))
async def callback_album_chosen(callback: types.CallbackQuery):
    callback_data = callback.data.strip('!').split('!')[1:]
    artist_id = ''
    if len(callback_data) == 2:
        album_id, search_id = callback_data
    else:
        album_id, search_id, artist_id = callback_data
    try:
        (
            album_title,
            tracks_results,
            tracks_titles_output,
            left_btn,
            right_btn,
            pager,
        ) = await get_album(album_id)
    except Exception:
        return await callback.answer(text='❌ Альбом не найден.')
    await callback.message.edit_text(
        text=(
            f'<b>🎧 {quote_html(album_title)}</b> '
            f'({min(((pager["page"] + 1) * pager["per_page"], pager["total"]))} из {pager["total"]})\n\n'
            f'{tracks_titles_output}'
        ),
        reply_markup=generate_album_keyboard(
            results=tracks_results,
            album_id=album_id,
            left=left_btn,
            right=right_btn,
            search_id=search_id,
            artist_id=artist_id,
        ),
    )


@dp.callback_query_handler(Text(startswith="!playlist!"))
async def callback_playlist_chosen(callback: types.CallbackQuery):
    playlist_id = callback.data[10:][:callback.data[10:].find('!')]
    search_id = callback.data[10:][callback.data[10:].find('!') + 1:]
    try:
        (
            playlist_title,
            tracks_results,
            tracks_titles_output,
            left_btn,
            right_btn,
            pager,
        ) = await get_playlist(playlist_id)
    except Exception:
        return await callback.answer(text='❌ Плейлист не найден.')
    await callback.message.edit_text(
        text=(
            f'<b>🎧 {quote_html(playlist_title)}</b> '
            f'({min(((pager["page"] + 1) * pager["per_page"], pager["total"]))} из {pager["total"]})\n\n'
            f'{tracks_titles_output}'
        ),
        reply_markup=generate_playlist_keyboard(tracks_results, playlist_id, left_btn, right_btn, search_id),
    )


@dp.callback_query_handler(Text(startswith='$'))
async def callback_change_artist_page(callback: types.CallbackQuery):
    _page_artist_ids = callback.data[1:][:callback.data[1:].find('!')]
    search_id = callback.data[1:][callback.data[1:].find('!') + 1:]
    page_id, artist_id = map(int, _page_artist_ids.split('~'))
    (
        artist_name,
        tracks_results,
        tracks_titles_output,
        left_btn,
        right_btn,
        pager,
    ) = await get_artist(artist_id, page_id)

    await callback.message.edit_text(
        text=(
            f'<b>🎧 {quote_html(artist_name)}</b> '
            f'({min(((pager["page"] + 1) * pager["per_page"], pager["total"]))} из {pager["total"]})\n\n'
            f'{tracks_titles_output}'
        ),
        reply_markup=generate_artist_keyboard(tracks_results, artist_id, left_btn, right_btn, search_id),
    )


@dp.callback_query_handler(Text(startswith='%'))
async def callback_change_album_page(callback: types.CallbackQuery):
    page_id = int(callback.data[1:][:callback.data.find('~') - 1])
    
    callback_data = callback.data[callback.data.find('~') + 1:].split('!')
    artist_id = ''
    if len(callback_data) == 2:
        album_id, search_id = callback_data
    else:
        album_id, search_id, artist_id = callback_data

    (
        album_title,
        tracks_results,
        tracks_titles_output,
        left_btn,
        right_btn,
        pager,
    ) = await get_album(album_id, page_id)

    await callback.message.edit_text(
        text=(
            f'<b>🎧 {quote_html(album_title)}</b> '
            f'({min(((pager["page"] + 1) * pager["per_page"], pager["total"]))} из {pager["total"]})\n\n'
            f'{tracks_titles_output}'
        ),
        reply_markup=generate_album_keyboard(tracks_results, album_id, left_btn, right_btn, search_id, artist_id),
    )


@dp.callback_query_handler(Text(startswith='@'))
async def callback_change_playlist_page(callback: types.CallbackQuery):
    search_id = callback.data[1:][callback.data[1:].find('!') + 1:]
    page_id, playlist_id = callback.data[1:][:callback.data[1:].find('!')].split('~')
    (
        playlist_title,
        tracks_results,
        tracks_titles_output,
        left_btn,
        right_btn,
        pager,
    ) = await get_playlist(playlist_id, int(page_id))

    await callback.message.edit_text(
        text=(
            f'<b>🎧 {quote_html(playlist_title)}</b> '
            f'({min(((pager["page"] + 1) * pager["per_page"], pager["total"]))} из {pager["total"]})\n\n'
            f'{tracks_titles_output}'
        ),
        reply_markup=generate_playlist_keyboard(tracks_results, playlist_id, left_btn, right_btn, search_id),
    )
