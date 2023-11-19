from aiogram.types import Message, InputFile
from config import DATABASE
from database import User
from dispather import dp
from filters import IsOwnerFilter
from stats_logs import new_mailing_log


@dp.message_handler(IsOwnerFilter(), commands=['admin'])
async def admin_help(message: Message) -> None:
    await message.answer(
        '<b>Панель администратора</b>\n'
        '\n'
        '/count_users - Количество зарегистрированных пользователей\n'
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
