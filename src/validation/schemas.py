import math
from datetime import date
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field, field_validator

from src.domain.enums import EntityType, TransactionType


class TransactionImportSchema(BaseModel):
    transaction_id: str = Field(min_length=1)
    date: date
    entity_type: EntityType
    entity_name: str = Field(min_length=1)
    transaction_type: TransactionType
    category: str = Field(min_length=1)
    description: str
    amount: Decimal = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)
    source_account: str = Field(min_length=1)
    destination_account: str = Field(min_length=1)
    # Entidade de contraparte para fluxos cruzados PF<->PJ.
    # Opcional: quando ausente em fluxos cruzados, um nome derivado e gerado.
    counter_entity_name: str | None = None

    @field_validator("counter_entity_name", mode="before")
    @classmethod
    def _coerce_nan_to_none(cls, v: Any) -> str | None:
        if v is None:
            return None
        if isinstance(v, float) and math.isnan(v):
            return None
        s = str(v).strip()
        return s if s else None
