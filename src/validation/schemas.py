import math
from datetime import date
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.domain.enums import EntityType, IncomeSourceType, TransactionType


class TransactionImportSchema(BaseModel):
    id_lancamento: str = Field(min_length=1)
    data: date
    tipo_entidade: EntityType
    nome_entidade: str = Field(min_length=1)
    tipo_transacao: TransactionType
    categoria: str = Field(min_length=1)
    descricao: str
    valor: Decimal = Field(gt=0)
    moeda: str = Field(min_length=3, max_length=3)
    conta_origem: str = Field(min_length=1)
    conta_destino: str = Field(min_length=1)
    # Entidade de contraparte para fluxos cruzados PF<->PJ.
    # Opcional: quando ausente em fluxos cruzados, um nome derivado é gerado.
    nome_contraparte: str | None = None

    @field_validator("nome_contraparte", mode="before")
    @classmethod
    def _coerce_nan_to_none(cls, v: Any) -> str | None:
        if v is None:
            return None
        if isinstance(v, float) and math.isnan(v):
            return None
        s = str(v).strip()
        return s if s else None


class ManualTransactionInput(BaseModel):
    """Schema de validação para lançamento manual via formulário."""

    model_config = ConfigDict(str_strip_whitespace=True)

    source_entity_id: int = Field(gt=0)
    source_account_id: int = Field(gt=0)
    destination_account_id: int = Field(gt=0)
    transaction_date: date
    category_id: int = Field(gt=0)
    description: str = ""
    amount: Decimal = Field(gt=Decimal("0"))
    transaction_type: TransactionType
    currency: str = Field(default="BRL", min_length=3, max_length=3)


class IncomeSourceInput(BaseModel):
    """Schema de validação para cadastro de fonte de renda."""

    model_config = ConfigDict(str_strip_whitespace=True)

    entity_id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=255)
    source_type: IncomeSourceType
    expected_monthly_amount: Decimal | None = Field(default=None, ge=Decimal("0"))


class BudgetInput(BaseModel):
    """Schema de validação para definição de meta de gasto mensal."""

    model_config = ConfigDict(str_strip_whitespace=True)

    category_id: int = Field(gt=0)
    year_month: str = Field(
        min_length=7,
        max_length=7,
        pattern=r"^\d{4}-\d{2}$",
        description="Período no formato YYYY-MM",
    )
    limit_amount: Decimal = Field(gt=Decimal("0"))
