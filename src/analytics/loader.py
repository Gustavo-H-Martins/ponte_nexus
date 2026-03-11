import pandas as pd
from sqlalchemy import text

from src.config.database import engine

_TRANSACTIONS_QUERY = text(
    """
    SELECT
        t.id,
        t.external_transaction_id AS transaction_id,
        t.transaction_date         AS date,
        t.transaction_type,
        t.description,
        CAST(t.amount AS FLOAT)    AS amount,
        t.currency,
        c.name                     AS category,
        sa.account_name            AS source_account,
        da.account_name            AS destination_account,
        se.name                    AS source_entity_name,
        se.entity_type             AS source_entity_type,
        de.name                    AS destination_entity_name,
        de.entity_type             AS destination_entity_type
    FROM lancamentos t
    JOIN categorias c  ON c.id  = t.category_id
    JOIN contas     sa ON sa.id = t.source_account_id
    JOIN contas     da ON da.id = t.destination_account_id
    JOIN entidades  se ON se.id = t.source_entity_id
    JOIN entidades  de ON de.id = t.destination_entity_id
    ORDER BY t.transaction_date DESC
    """
)


def load_transactions_df() -> pd.DataFrame:
    """Carrega todas as transacoes com entidades, contas e categorias resolvidas.

    Retorna DataFrame vazio com colunas tipadas quando nao ha registros.
    """
    with engine.connect() as conn:
        df = pd.read_sql(_TRANSACTIONS_QUERY, conn)

    if df.empty:
        return df

    df["date"] = pd.to_datetime(df["date"])
    df["amount"] = df["amount"].astype(float)
    return df
