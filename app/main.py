
from fastapi import FastAPI
from pydantic import BaseModel, Field, field_validator, model_validator

app = FastAPI(
    title="FinSecure Pay Transaction Validation API",
    description="API for validating payment transactions.",
    version="1.0.0",
)


class Transaction(BaseModel):
    transaction_id: str = Field(min_length=1, max_length=100)
    amount: float = Field(gt=0, allow_inf_nan=False)
    currency: str
    sender_account: str = Field(min_length=1, max_length=100)
    receiver_account: str = Field(min_length=1, max_length=100)

    @field_validator("transaction_id", "sender_account", "receiver_account")
    @classmethod
    def reject_blank_strings(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field must not be blank")
        return value

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, value: str) -> str:
        value = value.upper()
        if value not in {"SGD", "USD", "EUR"}:
            raise ValueError("Currency must be SGD, USD, or EUR")
        return value

    @model_validator(mode="after")
    def validate_accounts(self):
        if self.sender_account == self.receiver_account:
            raise ValueError(
                "Sender and receiver accounts must be different"
            )
        return self


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/validate")
def validate_transaction(transaction: Transaction):
    return {
        "valid": True,
        "message": "Transaction passed validation",
        "transaction": transaction.model_dump(),
    }
