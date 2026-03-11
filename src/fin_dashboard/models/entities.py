from datetime import date
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import Date, Enum, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from src.fin_dashboard.core.database import Base


class TransactionType(StrEnum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(100), index=True)
    occurred_on: Mapped[date] = mapped_column(Date, index=True)
    description: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(100), index=True)
    tx_type: Mapped[TransactionType] = mapped_column(Enum(TransactionType), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    account: Mapped[str | None] = mapped_column(String(100), nullable=True)
