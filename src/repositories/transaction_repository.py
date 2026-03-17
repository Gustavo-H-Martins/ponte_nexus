from sqlalchemy import func, select

from src.models.db_models import TransactionModel
from src.repositories.base import BaseRepository


class TransactionRepository(BaseRepository):
    def add(self, tx: TransactionModel) -> None:
        if tx.owner_id is None:
            tx.owner_id = self.owner_id
        self.session.add(tx)

    def add_many(self, transactions: list[TransactionModel]) -> None:
        for tx in transactions:
            if tx.owner_id is None:
                tx.owner_id = self.owner_id
        self.session.add_all(transactions)

    def exists_by_external_id(self, external_id: str) -> bool:
        stmt = self._owner_filter(
            select(TransactionModel).where(TransactionModel.external_transaction_id == external_id),
            TransactionModel,
        )
        return self.session.scalar(stmt) is not None

    def count(self) -> int:
        stmt = self._owner_filter(
            select(func.count()).select_from(TransactionModel), TransactionModel
        )
        return self.session.scalar(stmt) or 0
