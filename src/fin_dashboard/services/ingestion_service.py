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
                    nome_entidade=r.nome_entidade,
                    data=r.data,
                    descricao=r.descricao,
                    categoria=r.categoria,
                    tipo_transacao=r.tipo_transacao,
                    valor=Decimal(r.valor),
                    conta_origem=r.conta_origem,
                )
                for r in records
            ]
        )
        session.commit()
    return len(records)
