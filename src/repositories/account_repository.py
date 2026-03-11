from sqlalchemy import select

from src.models.db_models import AccountModel
from src.repositories.base import BaseRepository


class AccountRepository(BaseRepository):
    def get_by_name_and_entity(self, account_name: str, entity_id: int) -> AccountModel | None:
        stmt = select(AccountModel).where(
            AccountModel.account_name == account_name,
            AccountModel.entity_id == entity_id,
        )
        return self.session.scalar(stmt)

    def get_or_create(
        self, account_name: str, entity_id: int, currency: str = "BRL"
    ) -> AccountModel:
        existing = self.get_by_name_and_entity(account_name, entity_id)
        if existing:
            return existing
        account = AccountModel(
            account_name=account_name, entity_id=entity_id, currency=currency
        )
        self.session.add(account)
        self.session.flush()
        return account
