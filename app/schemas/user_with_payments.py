from typing import List
from .user import UserResponse
from .payment import PaymentResponse


class UserWithPaymentsResponse(UserResponse):
    payments: List[PaymentResponse]
