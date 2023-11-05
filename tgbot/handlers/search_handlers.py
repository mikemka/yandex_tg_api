from aiogram import types
from aiogram.dispatcher.filters import Text
from config import ENG_TO_RUS_TYPE, SEARCH_TYPES
from dispather import dp
from filters import SearchTypeFilter
from keyboards import generate_search_keyboard
from yandex import search as search_song
from user_info import get_search_type, next_search_type, save_search_request, get_search_request


async def callback_main_search(callback: types.CallbackQuery, need_next_search_type=True):
    search_request_id = callback.data[callback.data.find(':') + 1:]
    search_request = get_search_request(search_request_id)
    
    if search_request is None:
        return await callback.answer('Запрос устарел! Введите снова.')

    if need_next_search_type:
        next_search_type(callback.from_user.id)
    
    match get_search_type(callback.from_user.id):
        case 0:
            await search_type_track_callback(
                callback=callback,
                search_request=search_request,
                search_request_id=search_request_id,
            )
        case _:
            await search_type_other_callback(
                callback=callback,
                search_request=search_request,
                search_request_id=search_request_id,
            )


@dp.callback_query_handler(Text(startswith='search'))
async def callback_back_to_search(callback: types.CallbackQuery):
    await callback_main_search(callback=callback, need_next_search_type=False)


@dp.callback_query_handler(Text(startswith='next_search_type'))
async def callback_next_search_type(callback: types.CallbackQuery):
    await callback_main_search(callback=callback)


@dp.message_handler(SearchTypeFilter(requested_search_type='track'))
async def message_search_type_track(message: types.Message) -> None:
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
        reply_markup=generate_search_keyboard(
            results=info_for_keyboard,
            user_id=message.from_user.id,
            search_id=save_search_request(message.text),
        ),
    )


@dp.message_handler()
async def message_search_type_other(message: types.Message) -> None:
    message_text = (
        '<b>🔎 Результаты поиска</b>\n\n'
        '⬇️ Лучшее совпадение\n\n'
    )
    searching_state = SEARCH_TYPES[get_search_type(message.from_user.id)]
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
        'main_type': searching_state,
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
        message_text += f'<code>{index}.</code> <b>{val[1]}</b> – <i>[{ENG_TO_RUS_TYPE[searching_state]}]</i>\n'

    await message.reply(
        text=message_text,
        reply=False,
        reply_markup=generate_search_keyboard(
            results=info_for_keyboard,
            user_id=message.from_user.id,
            search_id=save_search_request(message.text),
        ),
    )


async def search_type_track_callback(
    callback: types.CallbackQuery,
    search_request: str,
    search_request_id: str,
):
    message_text = (
        '<b>🔎 Результаты поиска</b>\n\n'
        '⬇️ Лучшее совпадение\n\n'
    )
    searching_state = 'track'
    results = await search_song(search_request, search_type=searching_state)
    
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

    await callback.message.edit_text(
        text=message_text,
        reply_markup=generate_search_keyboard(
            results=info_for_keyboard,
            user_id=callback.from_user.id,
            search_id=search_request_id,
        ),
    )


async def search_type_other_callback(
    callback: types.CallbackQuery,
    search_request: str,
    search_request_id: str,
):
    message_text = (
        '<b>🔎 Результаты поиска</b>\n\n'
        '⬇️ Лучшее совпадение\n\n'
    )
    searching_state = SEARCH_TYPES[get_search_type(callback.from_user.id)]
    results = await search_song(search_request, search_type=searching_state)
    
    info_for_keyboard = {
        'best_result': None,
        'best_type': results['best_type'],
        'main_result': [],
        'main_type': searching_state,
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
        message_text += f'<code>{index}.</code> <b>{val[1]}</b> – <i>[{ENG_TO_RUS_TYPE[searching_state]}]</i>\n'

    await callback.message.edit_text(
        text=message_text,
        reply_markup=generate_search_keyboard(
            results=info_for_keyboard,
            user_id=callback.from_user.id,
            search_id=search_request_id,
        ),
    )
