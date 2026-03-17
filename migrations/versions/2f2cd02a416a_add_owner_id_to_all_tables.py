"""add_owner_id_to_all_tables

Revision ID: 2f2cd02a416a
Revises: 9f8ae896f01e
Create Date: 2026-03-16 21:15:19.374907

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2f2cd02a416a'
down_revision: Union[str, Sequence[str], None] = '9f8ae896f01e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(table: str, column: str) -> bool:
    bind = op.get_bind()
    rows = bind.execute(sa.text(f"PRAGMA table_info({table})")).fetchall()
    return any(row[1] == column for row in rows)


def _has_index(table: str, index_name: str) -> bool:
    bind = op.get_bind()
    rows = bind.execute(sa.text(f"PRAGMA index_list({table})")).fetchall()
    return any(row[1] == index_name for row in rows)


def _add_owner_id(table: str) -> None:
    """Adiciona owner_id e seu índice à tabela, se ainda não existirem."""
    index_name = f"ix_{table}_owner_id"
    if not _has_column(table, "owner_id"):
        op.add_column(table, sa.Column("owner_id", sa.Integer(), nullable=True))
    if not _has_index(table, index_name):
        op.create_index(index_name, table, ["owner_id"], unique=False)


def upgrade() -> None:
    """Upgrade schema.

    FKs omitidas — SQLite não suporta ADD CONSTRAINT via ALTER TABLE.
    A integridade referencial é garantida pela aplicação.
    Operações são idempotentes via verificação de PRAGMA.
    """
    for table in (
        "categorias",
        "contas",
        "empresas",
        "entidades",
        "fontes_renda",
        "lancamentos",
        "orcamentos",
        "relacionamentos_pf_pj",
    ):
        _add_owner_id(table)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_relacionamentos_pf_pj_owner_id'), table_name='relacionamentos_pf_pj')
    op.drop_column('relacionamentos_pf_pj', 'owner_id')
    op.drop_index(op.f('ix_orcamentos_owner_id'), table_name='orcamentos')
    op.drop_column('orcamentos', 'owner_id')
    op.drop_index(op.f('ix_lancamentos_owner_id'), table_name='lancamentos')
    op.drop_column('lancamentos', 'owner_id')
    op.drop_index(op.f('ix_fontes_renda_owner_id'), table_name='fontes_renda')
    op.drop_column('fontes_renda', 'owner_id')
    op.drop_index(op.f('ix_entidades_owner_id'), table_name='entidades')
    op.drop_column('entidades', 'owner_id')
    op.drop_index(op.f('ix_empresas_owner_id'), table_name='empresas')
    op.drop_column('empresas', 'owner_id')
    op.drop_index(op.f('ix_contas_owner_id'), table_name='contas')
    op.drop_column('contas', 'owner_id')
    op.drop_index(op.f('ix_categorias_owner_id'), table_name='categorias')
    op.drop_column('categorias', 'owner_id')
