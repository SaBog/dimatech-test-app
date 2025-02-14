from pydantic import BaseModel, ConfigDict
from datetime import datetime


class PaymentBase(BaseModel):
    transaction_id: str
    amount: float


class PaymentResponse(PaymentBase):
    id: int
    account_id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
