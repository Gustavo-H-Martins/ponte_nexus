from decimal import Decimal

from sqlalchemy import func, select

from src.models.db_models import AccountModel, EntityModel, TransactionModel
from src.repositories.base import BaseRepository


class AccountRepository(BaseRepository):
    def get_by_name_and_entity(self, account_name: str, entity_id: int) -> AccountModel | None:
        stmt = self._owner_filter(
            select(AccountModel).where(
                AccountModel.account_name == account_name,
                AccountModel.entity_id == entity_id,
            ),
            AccountModel,
        )
        return self.session.scalar(stmt)

    def get_or_create(
        self, account_name: str, entity_id: int, currency: str = "BRL"
    ) -> AccountModel:
        existing = self.get_by_name_and_entity(account_name, entity_id)
        if existing:
            return existing
        account = AccountModel(
            account_name=account_name, entity_id=entity_id, currency=currency,
            owner_id=self.owner_id,
        )
        self.session.add(account)
        self.session.flush()
        return account

    def list_all(self) -> list[AccountModel]:
        stmt = self._owner_filter(select(AccountModel).order_by(AccountModel.account_name), AccountModel)
        return list(self.session.scalars(stmt))

    def list_active(self) -> list[AccountModel]:
        """Retorna apenas contas ativas, ordenadas por nome."""
        stmt = self._owner_filter(
            select(AccountModel)
            .where(AccountModel.is_active == True)  # noqa: E712
            .order_by(AccountModel.account_name),
            AccountModel,
        )
        return list(self.session.scalars(stmt))

    def list_by_entity(self, entity_id: int) -> list[AccountModel]:
        stmt = self._owner_filter(
            select(AccountModel)
            .where(AccountModel.entity_id == entity_id)
            .order_by(AccountModel.account_name),
            AccountModel,
        )
        return list(self.session.scalars(stmt))

    def create(
        self,
        account_name: str,
        entity_id: int,
        account_type: str = "conta_bancaria",
        currency: str = "BRL",
        description: str | None = None,
    ) -> AccountModel:
        """Cria uma nova conta. Lança ValueError se já existir conta com mesmo nome na entidade."""
        if self.get_by_name_and_entity(account_name, entity_id):
            raise ValueError(f"Conta '{account_name}' já existe para esta entidade.")
        account = AccountModel(
            account_name=account_name,
            entity_id=entity_id,
            account_type=account_type,
            currency=currency,
            description=description,
            owner_id=self.owner_id,
        )
        self.session.add(account)
        self.session.flush()
        return account

    def deactivate(self, account_id: int) -> None:
        """Desativa uma conta sem apagar o histórico de transações."""
        account = self.session.get(AccountModel, account_id)
        if account:
            account.is_active = False
            self.session.flush()

    def delete_by_id(self, account_id: int) -> None:
        account = self.session.get(AccountModel, account_id)
        if account:
            self.session.delete(account)
            self.session.flush()

    def list_with_entity(self) -> list[dict]:
        """Retorna contas com dados da entidade vinculada e saldo calculado."""
        stmt = (
            select(AccountModel, EntityModel)
            .join(EntityModel, AccountModel.entity_id == EntityModel.id)
            .order_by(EntityModel.name, AccountModel.account_name)
        )
        if self.owner_id is not None:
            stmt = stmt.where(AccountModel.owner_id == self.owner_id)
        rows = self.session.execute(stmt).all()

        balances = self.balances_by_account()

        return [
            {
                "id": acc.id,
                "account_name": acc.account_name,
                "account_type": acc.account_type,
                "entity_id": acc.entity_id,
                "currency": acc.currency,
                "description": acc.description,
                "is_active": acc.is_active,
                "entity_name": ent.name,
                "entity_type": ent.entity_type,
                "balance": balances.get(acc.id, Decimal("0")),
            }
            for acc, ent in rows
        ]

    def balances_by_account(self) -> dict[int, Decimal]:
        """Calcula saldo atual (entradas − saídas) por conta em uma única query."""
        credits_q = select(
            TransactionModel.destination_account_id.label("account_id"),
            TransactionModel.amount.label("signed"),
        )
        debits_q = select(
            TransactionModel.source_account_id.label("account_id"),
            (-TransactionModel.amount).label("signed"),
        )
        if self.owner_id is not None:
            credits_q = credits_q.where(TransactionModel.owner_id == self.owner_id)
            debits_q  = debits_q.where(TransactionModel.owner_id == self.owner_id)
        union = credits_q.union_all(debits_q).subquery()
        stmt = (
            select(union.c.account_id, func.sum(union.c.signed).label("balance"))
            .group_by(union.c.account_id)
        )
        rows = self.session.execute(stmt).all()
        return {row.account_id: Decimal(str(row.balance)) for row in rows}
