from datetime import date
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import Date, Enum, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from src.fin_dashboard.core.database import Base


class TransactionType(StrEnum):
    RECEITA              = "receita"
    DESPESA              = "despesa"
    TRANSFERENCIA_PF_PJ  = "transferencia_pf_pj"
    TRANSFERENCIA_PJ_PF  = "transferencia_pj_pf"
    APORTE_PF_PJ         = "aporte_pf_pj"
    EMPRESTIMO_PF_PJ     = "emprestimo_pf_pj"
    DIVIDENDOS           = "dividendos"
    PRO_LABORE           = "pro_labore"


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome_entidade: Mapped[str] = mapped_column(String(100), index=True)
    data: Mapped[date] = mapped_column(Date, index=True)
    descricao: Mapped[str] = mapped_column(String(255))
    categoria: Mapped[str] = mapped_column(String(100), index=True)
    tipo_transacao: Mapped[TransactionType] = mapped_column(Enum(TransactionType), index=True)
    valor: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    conta_origem: Mapped[str | None] = mapped_column(String(100), nullable=True)
