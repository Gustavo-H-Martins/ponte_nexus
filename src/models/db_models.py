from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from src.config.database import Base


FK_ENTITIES_ID   = "entidades.id"
FK_ACCOUNTS_ID   = "contas.id"
FK_CATEGORIES_ID = "categorias.id"
FK_USERS_ID      = "usuarios.id"


class EntityModel(Base):
    __tablename__ = "entidades"

    id:          Mapped[int]      = mapped_column(primary_key=True)
    owner_id:    Mapped[int|None] = mapped_column(ForeignKey(FK_USERS_ID), nullable=True, index=True)
    name:        Mapped[str]      = mapped_column(String(255), nullable=False)
    entity_type: Mapped[str]      = mapped_column(String(8),   nullable=False)


class AccountModel(Base):
    __tablename__ = "contas"

    id:           Mapped[int]      = mapped_column(primary_key=True)
    owner_id:     Mapped[int|None] = mapped_column(ForeignKey(FK_USERS_ID), nullable=True, index=True)
    entity_id:    Mapped[int]      = mapped_column(ForeignKey(FK_ENTITIES_ID), nullable=False)
    account_name: Mapped[str]      = mapped_column(String(255), nullable=False)
    account_type: Mapped[str]      = mapped_column(String(32), nullable=False, default="conta_bancaria")
    currency:     Mapped[str]      = mapped_column(String(3), nullable=False)
    description:  Mapped[str|None] = mapped_column(Text, nullable=True)
    is_active:    Mapped[bool]     = mapped_column(default=True, nullable=False)


class CategoryModel(Base):
    __tablename__ = "categorias"

    id:             Mapped[int]      = mapped_column(primary_key=True)
    owner_id:       Mapped[int|None] = mapped_column(ForeignKey(FK_USERS_ID), nullable=True, index=True)
    name:           Mapped[str]      = mapped_column(String(255), nullable=False)
    category_group: Mapped[str]      = mapped_column(String(64),  nullable=False)


class TransactionModel(Base):
    __tablename__ = "lancamentos"

    id:                      Mapped[int]      = mapped_column(primary_key=True)
    owner_id:                Mapped[int|None] = mapped_column(ForeignKey(FK_USERS_ID), nullable=True, index=True)
    external_transaction_id: Mapped[str]      = mapped_column(String(128), nullable=False, unique=True)
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

    id:           Mapped[int]      = mapped_column(primary_key=True)
    owner_id:     Mapped[int|None] = mapped_column(ForeignKey(FK_USERS_ID), nullable=True, index=True)
    pf_entity_id: Mapped[int]      = mapped_column(ForeignKey(FK_ENTITIES_ID), nullable=False)
    pj_entity_id: Mapped[int] = mapped_column(ForeignKey(FK_ENTITIES_ID), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class CompanyModel(Base):
    """Dados adicionais de pessoa jurídica vinculada a uma entidade PJ."""

    __tablename__ = "empresas"

    id:        Mapped[int]      = mapped_column(primary_key=True)
    owner_id:  Mapped[int|None] = mapped_column(ForeignKey(FK_USERS_ID), nullable=True, index=True)
    entity_id: Mapped[int]      = mapped_column(ForeignKey(FK_ENTITIES_ID), nullable=False, unique=True)
    cnpj: Mapped[str] = mapped_column(String(18), nullable=False, unique=True)
    company_type: Mapped[str] = mapped_column(String(64), nullable=False, default="ltda")


class IncomeSourceModel(Base):
    """Fonte de renda nomeada vinculada a uma entidade — permite classificar de onde vem cada receita."""

    __tablename__ = "fontes_renda"

    id:        Mapped[int]      = mapped_column(primary_key=True)
    owner_id:  Mapped[int|None] = mapped_column(ForeignKey(FK_USERS_ID), nullable=True, index=True)
    entity_id: Mapped[int]      = mapped_column(ForeignKey(FK_ENTITIES_ID), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    expected_monthly_amount: Mapped[Numeric | None] = mapped_column(Numeric(14, 2), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class BudgetModel(Base):
    """Meta de gasto mensal por categoria — base para alertas de orçamento."""

    __tablename__ = "orcamentos"
    __table_args__ = (
        UniqueConstraint("category_id", "year_month", name="uq_budget_category_month"),
    )

    id:          Mapped[int]      = mapped_column(primary_key=True)
    owner_id:    Mapped[int|None] = mapped_column(ForeignKey(FK_USERS_ID), nullable=True, index=True)
    category_id: Mapped[int]      = mapped_column(ForeignKey(FK_CATEGORIES_ID), nullable=False)
    year_month: Mapped[str] = mapped_column(String(7), nullable=False)  # formato YYYY-MM
    limit_amount: Mapped[Numeric] = mapped_column(Numeric(14, 2), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class UserModel(Base):
    """Usuário do sistema com credenciais e permissões."""

    __tablename__ = "usuarios"

    id:            Mapped[int]  = mapped_column(primary_key=True)
    email:         Mapped[str]  = mapped_column(String(255), nullable=False, unique=True)
    username:      Mapped[str]  = mapped_column(String(100), nullable=False)
    password_hash: Mapped[str]  = mapped_column(String(255), nullable=False)
    role:          Mapped[str]  = mapped_column(String(16),  nullable=False, default="user")
    plan:          Mapped[str]  = mapped_column(String(16),  nullable=False, default="free")
    is_active:     Mapped[bool] = mapped_column(Boolean,     nullable=False, default=True)
    created_at:    Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class ShareModel(Base):
    """Compartilhamento: um owner libera leitura dos seus dados para um reader."""

    __tablename__ = "compartilhamentos"
    __table_args__ = (
        UniqueConstraint("owner_id", "reader_id", name="uq_share_owner_reader"),
    )

    id:        Mapped[int]      = mapped_column(primary_key=True)
    owner_id:  Mapped[int]      = mapped_column(ForeignKey(FK_USERS_ID), nullable=False, index=True)
    reader_id: Mapped[int]      = mapped_column(ForeignKey(FK_USERS_ID), nullable=False, index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
