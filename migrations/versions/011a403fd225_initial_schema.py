"""initial_schema

Revision ID: 011a403fd225
Revises: 
Create Date: 2026-03-15 23:41:55.544715

Schema inicial do Ponte Nexus — reflete o estado criado por Base.metadata.create_all().
Este migration NÃO é aplicado ao banco de desenvolvimento existente.
Use `alembic stamp head` para marcar um banco já inicializado como atualizado.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '011a403fd225'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Cria o schema inicial completo."""
    op.create_table(
        "entidades",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("entity_type", sa.String(length=8), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "contas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("account_name", sa.String(length=255), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.ForeignKeyConstraint(["entity_id"], ["entidades.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "categorias",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("category_group", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "lancamentos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("external_transaction_id", sa.String(length=128), nullable=False),
        sa.Column("transaction_date", sa.Date(), nullable=False),
        sa.Column("transaction_type", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("amount", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("source_account_id", sa.Integer(), nullable=False),
        sa.Column("destination_account_id", sa.Integer(), nullable=False),
        sa.Column("source_entity_id", sa.Integer(), nullable=False),
        sa.Column("destination_entity_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categorias.id"]),
        sa.ForeignKeyConstraint(["destination_account_id"], ["contas.id"]),
        sa.ForeignKeyConstraint(["destination_entity_id"], ["entidades.id"]),
        sa.ForeignKeyConstraint(["source_account_id"], ["contas.id"]),
        sa.ForeignKeyConstraint(["source_entity_id"], ["entidades.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("external_transaction_id"),
    )
    op.create_table(
        "relacionamentos_pf_pj",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pf_entity_id", sa.Integer(), nullable=False),
        sa.Column("pj_entity_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["pf_entity_id"], ["entidades.id"]),
        sa.ForeignKeyConstraint(["pj_entity_id"], ["entidades.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "empresas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("cnpj", sa.String(length=18), nullable=False),
        sa.Column("company_type", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(["entity_id"], ["entidades.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cnpj"),
        sa.UniqueConstraint("entity_id"),
    )
    op.create_table(
        "fontes_renda",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("source_type", sa.String(length=64), nullable=False),
        sa.Column("expected_monthly_amount", sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["entity_id"], ["entidades.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "orcamentos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("year_month", sa.String(length=7), nullable=False),
        sa.Column("limit_amount", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categorias.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("category_id", "year_month", name="uq_budget_category_month"),
    )


def downgrade() -> None:
    """Remove todas as tabelas do schema inicial."""
    op.drop_table("orcamentos")
    op.drop_table("fontes_renda")
    op.drop_table("empresas")
    op.drop_table("relacionamentos_pf_pj")
    op.drop_table("lancamentos")
    op.drop_table("categorias")
    op.drop_table("contas")
    op.drop_table("entidades")
