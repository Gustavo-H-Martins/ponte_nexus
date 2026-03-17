import logging
from datetime import date
from decimal import Decimal
from typing import Any

import pandas as pd
from sqlalchemy.orm import Session

from src.config.database import SessionLocal
from src.ingestion.pipeline import IngestionPipeline
from src.models.db_models import TransactionModel
from src.repositories.account_repository import AccountRepository
from src.repositories.category_repository import CategoryRepository
from src.repositories.entity_repository import EntityRepository
from src.repositories.transaction_repository import TransactionRepository

logger = logging.getLogger(__name__)

_PF_TO_PJ = {"transferencia_pf_pj", "aporte_pf_pj", "emprestimo_pf_pj"}
_PJ_TO_PF = {"transferencia_pj_pf", "dividendos", "pro_labore"}


class IngestionService:
    def __init__(
        self, pipeline: IngestionPipeline, session_factory=SessionLocal, owner_id: int | None = None
    ) -> None:
        self.pipeline = pipeline
        self.session_factory = session_factory
        self.owner_id = owner_id

    def ingest_upload(self, filename: str, file_bytes: bytes) -> dict[str, Any]:
        """Valida e persiste registros a partir de bytes de um arquivo enviado via UI."""
        result, df = self.pipeline.run_upload(filename, file_bytes)
        if result["status"] == "failed":
            return result
        return self._persist_and_update(result, df)

    def ingest_file(self, file_path: str) -> dict[str, Any]:
        """Valida e persiste registros a partir de um caminho de arquivo."""
        with open(file_path, "rb") as f:
            file_bytes = f.read()
        result, df = self.pipeline.run_upload(filename=file_path, file_bytes=file_bytes)
        if result["status"] == "failed":
            return result
        return self._persist_and_update(result, df)

    def _persist_and_update(
        self, result: dict[str, Any], df: pd.DataFrame
    ) -> dict[str, Any]:
        with self.session_factory() as session:
            inserted, skipped = self._persist(df, session)
            session.commit()

        result["records_inserted"] = inserted
        result["records_skipped"] = skipped
        return result

    def _persist(self, df: pd.DataFrame, session: Session) -> tuple[int, int]:
        entity_repo   = EntityRepository(session, self.owner_id)
        account_repo  = AccountRepository(session, self.owner_id)
        category_repo = CategoryRepository(session, self.owner_id)
        tx_repo       = TransactionRepository(session, self.owner_id)

        inserted = 0
        skipped = 0

        for row in df.to_dict(orient="records"):
            external_id = str(row["id_lancamento"])

            if tx_repo.exists_by_external_id(external_id):
                skipped += 1
                continue

            tx_type    = str(row["tipo_transacao"])
            entity_type = str(row["tipo_entidade"])
            entity_name = str(row["nome_entidade"])
            raw_counter = row.get("nome_contraparte")
            counter_name: str | None = (
                None
                if raw_counter is None or (
                    isinstance(raw_counter, float) and pd.isna(raw_counter)
                ) or str(raw_counter).strip() == ""
                else str(raw_counter).strip()
            )
            currency = str(row["moeda"])

            src_entity, dst_entity = self._resolve_entities(
                tx_type, entity_name, entity_type, counter_name, entity_repo
            )

            src_account = account_repo.get_or_create(
                str(row["conta_origem"]), src_entity.id, currency
            )
            dst_account = account_repo.get_or_create(
                str(row["conta_destino"]), dst_entity.id, currency
            )
            category = category_repo.get_or_create(str(row["categoria"]))

            tx_date = pd.Timestamp(row["data"]).date()

            tx_model = TransactionModel(
                external_transaction_id=external_id,
                transaction_date=tx_date,
                transaction_type=tx_type,
                description=str(row.get("descricao", "")),
                amount=Decimal(str(row["valor"])),
                currency=currency,
                category_id=category.id,
                source_account_id=src_account.id,
                destination_account_id=dst_account.id,
                source_entity_id=src_entity.id,
                destination_entity_id=dst_entity.id,
                owner_id=self.owner_id,
            )
            tx_repo.add(tx_model)
            inserted += 1

        logger.info(
            "Persistência concluída: %d inseridos, %d ignorados (duplicata).",
            inserted,
            skipped,
        )
        return inserted, skipped

    @staticmethod
    def _resolve_entities(
        tx_type: str,
        entity_name: str,
        entity_type: str,
        counter_name: str | None,
        entity_repo: EntityRepository,
    ):
        if tx_type in _PF_TO_PJ:
            src = entity_repo.get_or_create(entity_name, "PF")
            dst = entity_repo.get_or_create(counter_name or f"{entity_name}_Empresa", "PJ")
        elif tx_type in _PJ_TO_PF:
            src = entity_repo.get_or_create(entity_name, "PJ")
            dst = entity_repo.get_or_create(counter_name or f"{entity_name}_responsavel", "PF")
        else:
            src = entity_repo.get_or_create(entity_name, entity_type)
            dst = src

        return src, dst


def create_ingestion_service(owner_id: int | None = None) -> IngestionService:
    return IngestionService(pipeline=IngestionPipeline(), session_factory=SessionLocal, owner_id=owner_id)
