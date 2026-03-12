from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from src.config.database import Base


FK_ENTITIES_ID = "entidades.id"
FK_ACCOUNTS_ID = "contas.id"
FK_CATEGORIES_ID = "categorias.id"


class EntityModel(Base):
    __tablename__ = "entidades"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(8), nullable=False)


class AccountModel(Base):
    __tablename__ = "contas"

    id: Mapped[int] = mapped_column(primary_key=True)
    entity_id: Mapped[int] = mapped_column(ForeignKey(FK_ENTITIES_ID), nullable=False)
    account_name: Mapped[str] = mapped_column(String(255), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)


class CategoryModel(Base):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category_group: Mapped[str] = mapped_column(String(64), nullable=False)


class TransactionModel(Base):
    __tablename__ = "lancamentos"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_transaction_id: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    transaction_date: Mapped[Date] = mapped_column(Date, nullable=False)
    transaction_type: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    amount: Mapped[Numeric] = mapped_column(Numeric(14, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey(FK_CATEGORIES_ID), nullable=False)
    source_account_id: Mapped[int] = mapped_column(ForeignKey(FK_ACCOUNTS_ID), nullable=False)
    destination_account_id: Mapped[int] = mapped_column(ForeignKey(FK_ACCOUNTS_ID), nullable=False)
    source_entity_id: Mapped[int] = mapped_column(ForeignKey(FK_ENTITIES_ID), nullable=False)
    destination_entity_id: Mapped[int] = mapped_column(ForeignKey(FK_ENTITIES_ID), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class PfPjRelationshipModel(Base):
    __tablename__ = "relacionamentos_pf_pj"

    id: Mapped[int] = mapped_column(primary_key=True)
    pf_entity_id: Mapped[int] = mapped_column(ForeignKey(FK_ENTITIES_ID), nullable=False)
    pj_entity_id: Mapped[int] = mapped_column(ForeignKey(FK_ENTITIES_ID), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class CompanyModel(Base):
    """Dados adicionais de pessoa jurídica vinculada a uma entidade PJ."""

    __tablename__ = "empresas"

    id: Mapped[int] = mapped_column(primary_key=True)
    entity_id: Mapped[int] = mapped_column(ForeignKey(FK_ENTITIES_ID), nullable=False, unique=True)
    cnpj: Mapped[str] = mapped_column(String(18), nullable=False, unique=True)
    company_type: Mapped[str] = mapped_column(String(64), nullable=False, default="ltda")
