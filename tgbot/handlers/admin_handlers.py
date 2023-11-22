from aiogram.types import Message, InputFile, MediaGroup
from config import DATABASE
from database import User
from dispather import dp
from filters import IsOwnerFilter
from stats_graphs import generate_downloaded_graph_image, generate_users_graph_image
from stats_logs import new_mailing_log
import os


@dp.message_handler(IsOwnerFilter(), commands=['admin'])
async def admin_help(message: Message) -> None:
    await message.answer(
        '<b>Панель администратора</b>\n'
        '\n'
        '/count_users - Количество зарегистрированных пользователей\n'
        '/stats - Получить статистику использования бота\n'
        '/get_database - Скачать базу данных в формате .sqlite3\n'
        '/test_mail <code>[текст сообщения, поддерживается html]</code> - Проверка отображения сообщения\n'
        '<code>/mail [текст сообщения, поддерживается html]</code> - Массовая рассылка сообщений\n',
    )


@dp.message_handler(IsOwnerFilter(), commands=['mail'])
async def mail(message: Message) -> None:
    _text, _users, _errors = message.text[6:], User.select(), 0
    users_list = []
    for _user in _users:
        local_error = 0
        try:
            await message.bot.send_message(chat_id=_user.user_id, text=_text)
        except:
            local_error = 1
        users_list += [(_user.user_id, (local_error + 1) % 2)]
        _errors += local_error
    
    new_mailing_log(admin_id=message.from_user.id, users_list=users_list)
    await message.answer(f'Отправлено {_users.count() - _errors} сообщения. {_errors} ошибок')


@dp.message_handler(IsOwnerFilter(), commands=['test_mail'])
async def test_mail(message: Message) -> None:
    _text = message.text[11:]
    try:
        await message.answer(text=_text)
    except:
        return await message.answer(f'Отправлено 0 сообщения. 1 ошибок')
    await message.answer(f'Отправлено 1 сообщения. 0 ошибок')


@dp.message_handler(IsOwnerFilter(), commands=['count_users'])
async def count_users(message: Message) -> None:
    await message.answer(f'Всего <b>{User.select().count()}</b> пользователей')


@dp.message_handler(IsOwnerFilter(), commands=['get_database'])
async def get_database(message: Message) -> None:
    await message.reply_document(
        document=InputFile(DATABASE, 'database.db'),
    )


@dp.message_handler(IsOwnerFilter(), commands=['stats'])
async def stats(message: Message) -> None:
    await message.bot.send_chat_action(message.chat.id, 'upload_photo')
    
    media = MediaGroup()
    graph_downloaded_7_path, graph_downloaded_7_all = generate_downloaded_graph_image(dates_count=7)
    graph_downloaded_14_path, graph_downloaded_14_all = generate_downloaded_graph_image(dates_count=14)
    graph_users_7_path, graph_users_7_all = generate_users_graph_image(dates_count=7)
    graph_users_14_path, graph_users_14_all = generate_users_graph_image(dates_count=14)
    for path in (
        graph_users_7_path,
        graph_users_14_path,
        graph_downloaded_7_path,
        graph_downloaded_14_path,
    ):
        media.attach_photo(InputFile(open(path, 'rb')))
        os.remove(path)
    
    _count_users = User.select().count()
    
    media_group = await message.reply_media_group(
        media=media,
        reply=False
    )
    await media_group[0].edit_caption(
        caption=(
            '<b>Статистика использования бота</b>\n'
            '\n'
            f'Всего зарегистрировано {_count_users} пользователей\n'
            f'За 7 дней зарегистрировано {graph_users_7_all} пользователей\n'
            f'За 14 дней зарегистрировано {graph_users_14_all} пользователей\n'
            '\n'
            f'За 7 дней скачано {graph_downloaded_7_all} треков\n'
            f'За 14 дней скачано {graph_downloaded_14_all} треков'
        )
    )
