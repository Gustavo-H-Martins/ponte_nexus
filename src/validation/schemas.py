import math
from datetime import date
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field, field_validator

from src.domain.enums import EntityType, TransactionType


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
