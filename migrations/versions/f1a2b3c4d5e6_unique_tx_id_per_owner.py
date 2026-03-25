"""unique_tx_id_per_owner

Revision ID: f1a2b3c4d5e6
Revises: be2a52eb5b28
Create Date: 2026-03-24 00:00:00.000000

Corrige a constraint de unicidade em external_transaction_id para ser scoped por
owner_id em vez de global. Isso permite que usuários distintos importem arquivos
com os mesmos IDs de lançamento sem conflito de unicidade.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'f1a2b3c4d5e6'
down_revision: Union[str, Sequence[str], None] = 'be2a52eb5b28'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove constraint unique global em external_transaction_id e cria
    constraint composta (owner_id, external_transaction_id)."""
    bind = op.get_bind()

    if bind.dialect.name == 'sqlite':
        # SQLite não suporta DROP CONSTRAINT. O único caminho é recriar a tabela.
        # A constraint sqlite_autoindex_* é implícita e não acessível por ALTER TABLE.
        op.execute(sa.text("DROP TABLE IF EXISTS lancamentos_new"))
        op.execute(sa.text("""
            CREATE TABLE lancamentos_new (
                id                       INTEGER      NOT NULL,
                owner_id                 INTEGER,
                external_transaction_id  VARCHAR(128) NOT NULL,
                transaction_date         DATE         NOT NULL,
                transaction_type         VARCHAR(64)  NOT NULL,
                description              TEXT,
                amount                   NUMERIC(14, 2) NOT NULL,
                currency                 VARCHAR(3)   NOT NULL,
                category_id              INTEGER      NOT NULL,
                source_account_id        INTEGER      NOT NULL,
                destination_account_id   INTEGER      NOT NULL,
                source_entity_id         INTEGER      NOT NULL,
                destination_entity_id    INTEGER      NOT NULL,
                created_at               DATETIME     NOT NULL DEFAULT (CURRENT_TIMESTAMP),
                PRIMARY KEY (id),
                UNIQUE (owner_id, external_transaction_id),
                FOREIGN KEY (owner_id)               REFERENCES usuarios(id),
                FOREIGN KEY (category_id)            REFERENCES categorias(id),
                FOREIGN KEY (source_account_id)      REFERENCES contas(id),
                FOREIGN KEY (destination_account_id) REFERENCES contas(id),
                FOREIGN KEY (source_entity_id)       REFERENCES entidades(id),
                FOREIGN KEY (destination_entity_id)  REFERENCES entidades(id)
            )
        """))
        op.execute(sa.text("""
            INSERT INTO lancamentos_new
            SELECT id, owner_id, external_transaction_id, transaction_date,
                   transaction_type, description, amount, currency,
                   category_id, source_account_id, destination_account_id,
                   source_entity_id, destination_entity_id,
                   COALESCE(created_at, DATETIME('now'))
            FROM lancamentos
        """))
        op.execute(sa.text("DROP TABLE lancamentos"))
        op.execute(sa.text("ALTER TABLE lancamentos_new RENAME TO lancamentos"))
        op.create_index('ix_lancamentos_owner_id', 'lancamentos', ['owner_id'])
    else:
        # PostgreSQL (Streamlit Cloud) — constraint name auto-gerada pelo PG.
        op.drop_constraint(
            'lancamentos_external_transaction_id_key',
            'lancamentos',
            type_='unique',
        )
        op.create_unique_constraint(
            'uq_tx_owner_external_id',
            'lancamentos',
            ['owner_id', 'external_transaction_id'],
        )


def downgrade() -> None:
    """Reverte para constraint única global em external_transaction_id."""
    op.drop_constraint('uq_tx_owner_external_id', 'lancamentos', type_='unique')
    op.create_unique_constraint(
        'lancamentos_external_transaction_id_key',
        'lancamentos',
        ['external_transaction_id'],
    )
