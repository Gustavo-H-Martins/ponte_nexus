from decimal import Decimal

from sqlalchemy import select

from src.models.db_models import IncomeSourceModel
from src.repositories.base import BaseRepository


class IncomeSourceRepository(BaseRepository):
    def list_by_entity(self, entity_id: int) -> list[IncomeSourceModel]:
        stmt = self._owner_filter(
            select(IncomeSourceModel)
            .where(IncomeSourceModel.entity_id == entity_id)
            .order_by(IncomeSourceModel.name),
            IncomeSourceModel,
        )
        return list(self.session.scalars(stmt))

    def list_active(self) -> list[IncomeSourceModel]:
        stmt = self._owner_filter(
            select(IncomeSourceModel)
            .where(IncomeSourceModel.is_active.is_(True))
            .order_by(IncomeSourceModel.name),
            IncomeSourceModel,
        )
        return list(self.session.scalars(stmt))

    def create(
        self,
        entity_id: int,
        name: str,
        source_type: str,
        expected_monthly_amount: Decimal | None = None,
    ) -> IncomeSourceModel:
        source = IncomeSourceModel(
            entity_id=entity_id,
            name=name,
            source_type=source_type,
            expected_monthly_amount=expected_monthly_amount,
            owner_id=self.owner_id,
        )
        self.session.add(source)
        self.session.flush()
        return source

    def deactivate(self, source_id: int) -> None:
        source = self.session.get(IncomeSourceModel, source_id)
        if source:
            source.is_active = False
            self.session.flush()
