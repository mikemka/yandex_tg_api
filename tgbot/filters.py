from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
import config


class IsOwnerFilter(BoundFilter):
    key = "is_owner"

    async def check(self, message: types.Message):
        return message.from_user.id in config.ADMIN_IDS
