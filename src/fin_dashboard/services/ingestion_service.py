from decimal import Decimal
from pathlib import Path

from src.fin_dashboard.core.database import SessionLocal
from src.fin_dashboard.ingestion.importers import read_csv
from src.fin_dashboard.models.entities import Transaction
from src.fin_dashboard.schemas.transaction import TransactionIn


def import_transactions(csv_path: Path) -> int:
    df = read_csv(csv_path)
    records = [TransactionIn(**row) for row in df.to_dict(orient="records")]

    with SessionLocal() as session:
        session.add_all(
            [
                Transaction(
                    source=r.source,
                    occurred_on=r.occurred_on,
                    description=r.description,
                    category=r.category,
                    tx_type=r.tx_type,
                    amount=Decimal(r.amount),
                    account=r.account,
                )
                for r in records
            ]
        )
        session.commit()
    return len(records)
