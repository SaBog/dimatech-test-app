from typing import List
from .user import UserResponse
from .account import AccountResponse


class UserWithAccountsResponse(UserResponse):
    accounts: List[AccountResponse]
