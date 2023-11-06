from aiogram import types
from aiogram.utils.markdown import quote_html
from database import User
from dispather import dp
from keyboards import generate_artist_keyboard, generate_album_keyboard, generate_playlist_keyboard
from re import match
from yandex import download_song, get_artist, get_album, get_playlist
from os import remove


@dp.message_handler(commands=['start', 'help'])
async def start(message: types.Message) -> None:
    if not User.select().where(User.user_id == message.from_user.id):
        User.create(user_id=message.from_user.id)
    
    await message.reply(
        text=(
            '<b>🎧 Yandex Music Bot</b>\n'
            '\n'
            'Слушайте и скачивайте треки с music.yandex.ru\n'
            'Введите название трека и скачайте его в <code>.mp3</code> файл.\n'
            '\n'
            '<b>⬇️ Как скачать трек:</b>\n'
            '- Введите название трека, исполнителя, альбом или плейлист\n'
            '- Отправьте ссылку на что угодно из <i>Яндекс.Музыка</i>\n'
            '- Вы можете найти трек по строчке из него\n'
        ),
        reply=False,
    )


@dp.message_handler(regexp=r'https?://music\.yandex\.ru/album/(\d+)/track/(\d+)')
async def song_by_link(message: types.Message) -> None:
    url = match(r'https?://music\.yandex\.ru/album/(\d+)/track/(\d+)', message.text)
    try:
        result = await download_song(url.group(1), url.group(2))
    except Exception:
        await message.delete()
        return await message.reply(
            text='❌ Возможно, песня была перемещена или удалена.',
            reply=False,
        )
    
    msg_ans = await message.reply(
        text='🎧 Скачиваем...',
        reply=False,
    )
    
    path, thumb_path, title, performer = result
    
    await message.bot.send_audio(
        message.chat.id,
        audio=open(path, 'rb'),
        caption='Скачано в <a href="https://t.me/yandexMusicDownload_bot">Yandex Music Bot</a>',
        performer=performer,
        title=title,
        thumb=open(thumb_path, 'rb'),
    )
    await msg_ans.delete()
    remove(path=path)
    remove(path=thumb_path)


@dp.message_handler(regexp=r'https?://music\.yandex\.ru/artist/(\d+)')
async def artist_by_link(message: types.Message) -> None:
    artist_id = match(r'https?://music\.yandex\.ru/artist/(\d+)', message.text).group(1)
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
        await message.delete()
        return await message.reply(
            text='❌ Исполнитель не найден.',
            reply=False,
        )
    await message.reply(
        text=(
            f'<b>🎧 {quote_html(artist_name)}</b> '
            f'({min(((pager["page"] + 1) * pager["per_page"], pager["total"]))} из {pager["total"]})\n\n'
            f'{tracks_titles_output}'
        ),
        reply=False,
        reply_markup=generate_artist_keyboard(tracks_results, artist_id, left_btn, right_btn),
    )


@dp.message_handler(regexp=r'https?://music\.yandex\.ru/album/(\d+)')
async def album_by_link(message: types.Message) -> None:
    album_id = match(r'https?://music\.yandex\.ru/album/(\d+)', message.text).group(1)
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
        await message.delete()
        return await message.reply(
            text='❌ Альбом не найден.',
            reply=False,
        )
    await message.reply(
        text=(
            f'<b>🎧 {quote_html(album_title)}</b> '
            f'({min(((pager["page"] + 1) * pager["per_page"], pager["total"]))} из {pager["total"]})\n\n'
            f'{tracks_titles_output}'
        ),
        reply=False,
        reply_markup=generate_album_keyboard(tracks_results, album_id, left_btn, right_btn),
    )


@dp.message_handler(regexp=r'https?://music\.yandex\.ru/users/(.+)/playlists/(\d+)')
async def playlist_by_link(message: types.Message) -> None:
    url = match(r'https?://music\.yandex\.ru/users/(.+)/playlists/(\d+)', message.text)
    playlist_id = f'{url.group(1)}:{url.group(2)}'
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
        await message.delete()
        return await message.reply(
            text='❌ Плейлист не найден.',
            reply=False,
        )
    await message.reply(
        text=(
            f'<b>🎧 {quote_html(playlist_title)}</b> '
            f'({min(((pager["page"] + 1) * pager["per_page"], pager["total"]))} из {pager["total"]})\n\n'
            f'{tracks_titles_output}'
        ),
        reply=False,
        reply_markup=generate_playlist_keyboard(tracks_results, playlist_id, left_btn, right_btn),
    )
