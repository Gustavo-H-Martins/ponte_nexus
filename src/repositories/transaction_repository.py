from sqlalchemy import func, select

from src.models.db_models import TransactionModel
from src.repositories.base import BaseRepository


class TransactionRepository(BaseRepository):
    def add(self, tx: TransactionModel) -> None:
        self.session.add(tx)

    def add_many(self, transactions: list[TransactionModel]) -> None:
        self.session.add_all(transactions)

    def exists_by_external_id(self, external_id: str) -> bool:
        stmt = select(TransactionModel).where(
            TransactionModel.external_transaction_id == external_id
        )
        return self.session.scalar(stmt) is not None

    def count(self) -> int:
        stmt = select(func.count()).select_from(TransactionModel)
        return self.session.scalar(stmt) or 0
