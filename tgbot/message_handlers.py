from aiogram import types
from aiogram.dispatcher.filters import Text
from database import User
from dispather import dp
from re import match
from keyboards import generate_keyboard
from yandex import download_song, search as search_song
from yandex_music.exceptions import BadRequestError


@dp.message_handler(commands=['start', 'help'])
async def start(message: types.Message) -> None:
    if not User.select().where(User.user_id == message.from_user.id):
        User.create(user_id=message.from_user.id)
    
    await message.reply(
        text=(
            '<b>🎧 Yandex Music Bot</b>\n'
            '\n'
            'Слушайте и скачивайте треки с music.yandex.ru\n'
            'Введите название трека и скачайте его в .mp3 файл.\n'
            '\n'
            '<b>⬇️ Как скачать трек:</b>\n'
            '- По названию или исполнителю\n'
            '- По ссылке на трек'
        ),
        reply=False,
    )


@dp.message_handler()
async def song(message: types.Message) -> None:
    url = match(r'https{0,1}://music\.yandex\.ru/album/(\d+)/track/(\d+)', message.text)
    if url:
        try:
            result = download_song(url.group(1), url.group(2))
        except BadRequestError:
            await message.delete()
            return await message.reply(text='❌ Возможно, песня была перемещена или удалена.', reply=False)
        
        path, thumb_path, title, performer = result
        
        return await message.bot.send_audio(
            message.chat.id,
            audio=open(path, 'rb'),
            caption='Скачано в <a href="https://t.me/yandexMusicDownload_bot">Yandex Music Bot</a>',
            performer=performer,
            title=title,
            thumb=open(thumb_path, 'rb'),
        )
    
    message_text = '<b>🔎 Результаты поиска</b>\n\n'
    results = search_song(message.text)
    if results is None:
        return await message.reply(text='❌ Ничего не нашлось. Попробуйте изменить свой запрос.', reply=False)
    for number, track in enumerate(results):
        message_text += f'<code>{number + 1}.</code> <b>{track["title"]}</b> – <i>{track["performer"]}</i>\n'
    
    await message.reply(
        text=message_text,
        reply_markup=generate_keyboard(results),
        reply=False,
    )


@dp.callback_query_handler(Text(startswith=">"))
async def callback_song_chosen(callback: types.CallbackQuery):
    try:
        result = download_song(*callback.data[1:].split(':')[::-1])
    except BadRequestError:
        return await callback.bot.send_message(
            chat_id=callback.from_user.id,
            text='❌ Возможно, песня была перемещена или удалена.',
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

