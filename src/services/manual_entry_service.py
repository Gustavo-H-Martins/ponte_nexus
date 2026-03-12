import logging
from uuid import uuid4

from src.config.database import SessionLocal
from src.models.db_models import AccountModel, TransactionModel
from src.validation.schemas import ManualTransactionInput

logger = logging.getLogger(__name__)


class ManualEntryService:
    """Persiste um único lançamento criado via formulário."""

    def __init__(self, session_factory=SessionLocal) -> None:
        self.session_factory = session_factory

    def create_transaction(self, data: ManualTransactionInput) -> None:
        """Valida referências e persiste o lançamento manual."""
        with self.session_factory() as session:
            dest_account = session.get(AccountModel, data.destination_account_id)
            if dest_account is None:
                raise ValueError("Conta de destino não encontrada no banco de dados.")

            tx = TransactionModel(
                external_transaction_id=f"manual-{uuid4()}",
                transaction_date=data.transaction_date,
                transaction_type=data.transaction_type.value,
                description=data.description,
                amount=data.amount,
                currency=data.currency,
                category_id=data.category_id,
                source_account_id=data.source_account_id,
                destination_account_id=data.destination_account_id,
                source_entity_id=data.source_entity_id,
                destination_entity_id=dest_account.entity_id,
            )
            session.add(tx)
            session.commit()
            logger.info("Lançamento manual criado: %s", tx.external_transaction_id)
