from pydantic import BaseModel, ConfigDict


class AccountBase(BaseModel):
    balance: float


class AccountResponse(AccountBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
