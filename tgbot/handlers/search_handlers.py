from aiogram import types
from config import ENG_TO_RUS_TYPE
from dispather import dp
from filters import SearchTypeFilter
from keyboards import generate_search_keyboard
from yandex import search as search_song
from user_info import get_search_type


@dp.message_handler(SearchTypeFilter(requested_search_type='track'))
async def search_type_track(message: types.Message) -> None:
    message_text = (
        '<b>🔎 Результаты поиска</b>\n\n'
        '⬇️ Лучшее совпадение\n\n'
    )
    searching_state = 'track'
    results = await search_song(message.text, search_type=searching_state)
    
    if results is None:
        await message.delete()
        return await message.reply(
            text='❌ Ничего не нашлось. Попробуйте сменить тип поиска или изменить свой запрос.',
            reply=False,
        )
    info_for_keyboard = {
        'best_result': None,
        'best_type': results['best_type'],
        'main_result': [],
        'main_type': 'track',
    }
    if results['best_type'] == 'track':
        track = info_for_keyboard['best_result'] = results["tracks"][0]
        message_text += f'<b>{track["title"]}</b> – <i>{track["performer"]}</i>\n\n'
    else:
        other = info_for_keyboard['best_result'] = results[results["best_type"] + "s"][0]
        message_text += f'<b>{other[1]}</b> – <i>[{ENG_TO_RUS_TYPE[results["best_type"]]}]</i>\n\n'
    
    for index, val in enumerate(
        results[f'{searching_state}s'][1 if results['best_type'] == searching_state else 0:],
        start=1,
    ):
        info_for_keyboard['main_result'] += [val]
        message_text += f'<code>{index}.</code> <b>{val["title"]}</b> – <i>{val["performer"]}</i>\n'

    await message.reply(
        text=message_text,
        reply=False,
        reply_markup=generate_search_keyboard(info_for_keyboard, message.from_user.id),
    )


@dp.message_handler()
async def search_type_other(message: types.Message) -> None:
    message_text = (
        '<b>🔎 Результаты поиска</b>\n\n'
        '⬇️ Лучшее совпадение\n\n'
    )
    searching_state = get_search_type(message.from_user.id)
    results = await search_song(message.text, search_type=searching_state)
    
    if results is None:
        await message.delete()
        return await message.reply(
            text='❌ Ничего не нашлось. Попробуйте сменить тип поиска или изменить свой запрос.',
            reply=False,
        )
    info_for_keyboard = {
        'best_result': None,
        'best_type': results['best_type'],
        'main_result': [],
        'main_type': 'track',
    }
    if results['best_type'] == 'track':
        track = info_for_keyboard['best_result'] = results["tracks"][0]
        message_text += f'<b>{track["title"]}</b> – <i>{track["performer"]}</i>\n\n'
    else:
        other = info_for_keyboard['best_result'] = results[results["best_type"] + "s"][0]
        message_text += f'<b>{other[1]}</b> – <i>[{ENG_TO_RUS_TYPE[results["best_type"]]}]</i>\n\n'
    
    for index, val in enumerate(
        results[f'{searching_state}s'][1 if results['best_type'] == searching_state else 0:],
        start=1,
    ):
        info_for_keyboard['main_result'] += [val]
        message_text += f'<code>{index}.</code> <b>{val[1]}</b> – <i>[{searching_state}]</i>\n'

    await message.reply(
        text=message_text,
        reply=False,
        reply_markup=generate_search_keyboard(info_for_keyboard, message.from_user.id),
    )
