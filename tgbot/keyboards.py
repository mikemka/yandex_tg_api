from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from config import ENG_TO_RUS_TYPE, SEARCH_TYPES
from user_info import get_search_type


def generate_search_keyboard(results: dict, user_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=5)
    match results['best_type']:
        case 'track':
            best_result_btn = InlineKeyboardButton(
                text=f'{results["best_result"]["title"]} – {results["best_result"]["performer"]}',
                callback_data=(
                    f'!track!{results["best_result"]["track_id"]}:{results["best_result"]["album_id"]}'
                ),
            )
        case _:
            best_result_btn = InlineKeyboardButton(
                text=f'{results["best_result"][1]} – [{ENG_TO_RUS_TYPE[results["best_type"]]}]',
                callback_data=f'!{results["best_type"]}!{results["best_result"][0]}',
            )
    keyboard.add(
        best_result_btn,
        InlineKeyboardButton(
            text=f'Тип: {ENG_TO_RUS_TYPE[SEARCH_TYPES[get_search_type(user_id)]].title()}',
            callback_data='next_search_type',
        )
    )
    results_btns = []
    for index, val in enumerate(results['main_result'], start=1):
        match results['main_type']:
            case 'track':
                callback = f'!track!{val["track_id"]}:{val["album_id"]}'
            case _:
                callback = f'!{results["best_type"]}!{val[0]}'
        results_btns += [InlineKeyboardButton(text=str(index), callback_data=callback)]
    return keyboard.add(*results_btns)


def generate_artist_keyboard(results: list, artist_id, left=True, right=True) -> InlineKeyboardMarkup:
    buttons = []
    keyboard = InlineKeyboardMarkup(row_width=5)
    for number, result in results:
        buttons += [InlineKeyboardButton(text=str(number), callback_data=f'>{result}')]
    keyboard.add(*buttons)
    x = results[0][0] // 10
    return keyboard.row(
        InlineKeyboardButton(text='«' if left else '', callback_data=f'${x - 1}~{artist_id}'),
        InlineKeyboardButton(text='»' if right else '', callback_data=f'${x + 1}~{artist_id}'),
    )
