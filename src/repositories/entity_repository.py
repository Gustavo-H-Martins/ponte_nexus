from sqlalchemy import select

from src.models.db_models import EntityModel
from src.repositories.base import BaseRepository


class EntityRepository(BaseRepository):
    def get_by_name_and_type(self, name: str, entity_type: str) -> EntityModel | None:
        stmt = select(EntityModel).where(
            EntityModel.name == name,
            EntityModel.entity_type == entity_type,
        )
        return self.session.scalar(stmt)

    def get_or_create(self, name: str, entity_type: str) -> EntityModel:
        existing = self.get_by_name_and_type(name, entity_type)
        if existing:
            return existing
        entity = EntityModel(name=name, entity_type=entity_type)
        self.session.add(entity)
        self.session.flush()
        return entity
