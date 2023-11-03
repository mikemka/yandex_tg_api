from aiogram import types
from aiogram.dispatcher.storage import FSMContext
from database import User
from dispather import dp
from re import match
from keyboards import generate_keyboard, generate_artist_keyboard
from yandex import download_song, search as search_song, get_artist
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
            '- Введите исполнителя или название трека\n'
            '- Отправьте ссылку на трек из <i>Яндекс.Музыка</i>\n'
            '- Вы можете найти трек по строчке из него\n'
        ),
        reply=False,
    )


@dp.message_handler(regexp=r'https{0,1}://music\.yandex\.ru/album/(\d+)/track/(\d+)')
async def song_by_link(message: types.Message) -> None:
    url = match(r'https{0,1}://music\.yandex\.ru/album/(\d+)/track/(\d+)', message.text)
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


@dp.message_handler(regexp=r'https{0,1}://music\.yandex\.ru/artist/(\d+)')
async def artist_by_link(message: types.Message) -> None:
    artist_id = match(r'https{0,1}://music\.yandex\.ru/artist/(\d+)', message.text).group(1)
    try:
        artist_name, tracks_results, tracks_titles_output, left_btn, right_btn = await get_artist(artist_id)
    except Exception:
        await message.delete()
        return await message.reply(
            text='❌ Исполнитель не найден.',
            reply=False,
        )
    await message.reply(
        text=f'<b>🎧 {artist_name}</b>\n\n{tracks_titles_output}',
        reply=False,
        reply_markup=generate_artist_keyboard(tracks_results, artist_id, left_btn, right_btn),
    )


@dp.message_handler(state="*")
async def search(message: types.Message, state: FSMContext) -> None:
    message_text = '<b>🔎 Результаты поиска</b>\n\n⬇️ Лучшее совпадение\n\n'
    searching_state = 'playlist'  # TODO
    results = await search_song(message.text, state=searching_state)
    
    if results['best_type'] is None:
        return await message.reply(
            text='❌ Ничего не нашлось. Попробуйте сменить тип поиска или изменить свой запрос.',
            reply=False,
        )
    
    x = {'album': 'альбом', 'artist': 'исполнитель', 'playlist': 'плейлист'}
    if results['best_type'] == 'track':
        track = results["tracks"][0]
        message_text += f'<b>{track["title"]}</b> – <i>{track["performer"]}</i>\n\n'
    else:
        message_text += (
            f'<b>{results[results["best_type"] + "s"][0][1]}</b> – <i>[{x[results["best_type"]]}]</i>\n\n'
        )
    
    for index, val in enumerate(
        results[f'{searching_state}s'][1 if results['best_type'] == searching_state else 0:],
        start=1,
    ):
        if searching_state == 'track':
            message_text += f'<code>{index}.</code> <b>{val["title"]}</b> – <i>{val["performer"]}</i>\n'
        else:
            message_text += f'<code>{index}.</code> <b>{val[1]}</b> – <i>[{x[searching_state]}]</i>\n'


    await message.reply(
        text=message_text,
        reply=False,
    )
