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
