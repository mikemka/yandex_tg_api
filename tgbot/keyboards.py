from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton


def generate_keyboard(results: list) -> InlineKeyboardMarkup:
    buttons = []
    for number, result in enumerate(results):
        buttons += [
            InlineKeyboardButton(str(number + 1), callback_data=f'>{result["track_id"]}:{result["album_id"]}')
        ]
    return InlineKeyboardMarkup(row_width=5).add(*buttons)
