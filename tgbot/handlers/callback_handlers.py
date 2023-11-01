from aiogram import types
from aiogram.dispatcher.filters import Text
from dispather import dp
from yandex import download_song
from yandex_music.exceptions import BadRequestError
from os import remove


@dp.callback_query_handler(Text(startswith=">"))
async def callback_song_chosen(callback: types.CallbackQuery):
    try:
        result = await download_song(*callback.data[1:].split(':')[::-1])
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
