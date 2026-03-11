from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

from src.fin_dashboard.models.entities import TransactionType


class TransactionIn(BaseModel):
    source: str = Field(min_length=1, max_length=100)
    occurred_on: date
    description: str = Field(min_length=1, max_length=255)
    category: str = Field(min_length=1, max_length=100)
    tx_type: TransactionType
    amount: Decimal
    account: str | None = Field(default=None, max_length=100)
