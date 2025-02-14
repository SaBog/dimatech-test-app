from pydantic import BaseModel, ConfigDict, Field


class PaymentWebhook(BaseModel):
    transaction_id: str = Field(...)
    account_id: int = Field(...)
    user_id: int = Field(...)
    amount: int = Field(...)
    signature: str = Field(...)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
                "user_id": 1,
                "account_id": 1,
                "amount": 100,
                "signature": "7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8",
            }
        }
    )
