from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

from src.fin_dashboard.models.entities import TransactionType


class TransactionIn(BaseModel):
    nome_entidade: str = Field(min_length=1, max_length=100)
    data: date
    descricao: str = Field(min_length=1, max_length=255)
    categoria: str = Field(min_length=1, max_length=100)
    tipo_transacao: TransactionType
    valor: Decimal
    conta_origem: str | None = Field(default=None, max_length=100)
