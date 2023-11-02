from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton


def generate_keyboard(results: list) -> InlineKeyboardMarkup:
    buttons = []
    keyboard = InlineKeyboardMarkup(row_width=5)
    for number, result in enumerate(results):
        if not number:
            keyboard.add(InlineKeyboardButton(
                f'{result["title"]} – {result["performer"]}',
                callback_data=f'>{result["track_id"]}:{result["album_id"]}'),
            )
            continue
        buttons += [
            InlineKeyboardButton(str(number), callback_data=f'>{result["track_id"]}:{result["album_id"]}')
        ]
    return keyboard.add(*buttons)


def generate_artist_keyboard(results: list, artist_id, left=True, right=True) -> InlineKeyboardMarkup:
    buttons = []
    keyboard = InlineKeyboardMarkup(row_width=5)
    for number, result in results:
        buttons += [InlineKeyboardButton(str(number), callback_data=f'>{result}')]
    keyboard.add(*buttons)
    x = results[0][0] // 10
    return keyboard.row(
        InlineKeyboardButton('«' if left else '', callback_data=f'${x - 1}~{artist_id}'),
        InlineKeyboardButton('»' if right else '', callback_data=f'${x + 1}~{artist_id}'),
    )
