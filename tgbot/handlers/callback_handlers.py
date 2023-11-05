from aiogram import types
from aiogram.dispatcher.filters import Text
from dispather import dp
from keyboards import generate_artist_keyboard
from yandex import download_song, get_artist
from yandex_music.exceptions import BadRequestError
from os import remove


@dp.callback_query_handler(Text(startswith="!track!"))
async def callback_track_chosen(callback: types.CallbackQuery):
    try:
        result = await download_song(*callback.data[7:].split(':')[::-1])
    except BadRequestError:
        return await callback.bot.send_message(
            chat_id=callback.from_user.id,
            text='❌ Возможно, песня была перемещена или удалена.',
        )
    
    msg_ans = await callback.bot.send_message(
        chat_id=callback.from_user.id,
        text='🎧 Скачиваем...',
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
    await msg_ans.delete()
    remove(path=path)
    remove(path=thumb_path)


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
            f'<b>🎧 {artist_name}</b> '
            f'({min(((pager["page"] + 1) * pager["per_page"], pager["total"]))} из {pager["total"]})\n\n'
            f'{tracks_titles_output}'
        ),
        reply_markup=generate_artist_keyboard(tracks_results, artist_id, left_btn, right_btn, search_id),
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
            f'<b>🎧 {artist_name}</b> '
            f'({min(((pager["page"] + 1) * pager["per_page"], pager["total"]))} из {pager["total"]})\n\n'
            f'{tracks_titles_output}'
        ),
        reply_markup=generate_artist_keyboard(tracks_results, artist_id, left_btn, right_btn, search_id),
    )
