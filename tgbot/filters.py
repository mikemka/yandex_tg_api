from aiogram import types
from aiogram.dispatcher.filters import BoundFilter, Filter
from config import ADMIN_IDS, SEARCH_TYPES
from user_info import get_search_type


class IsOwnerFilter(BoundFilter):
    key = "is_owner"

    async def check(self, message: types.Message):
        return message.from_user.id in ADMIN_IDS


class SearchTypeFilter(Filter):
    key = "search_type"

    def __init__(self, requested_search_type: int | str):
        self.requested_search_type = requested_search_type


    async def check(self, message: types.Message):
        if type(self.requested_search_type) == str: 
            self.requested_search_type = SEARCH_TYPES.index(self.requested_search_type)
        return get_search_type(message.from_user.id) == self.requested_search_type
