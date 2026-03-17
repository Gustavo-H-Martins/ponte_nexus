from sqlalchemy import select

from src.models.db_models import CategoryModel
from src.repositories.base import BaseRepository


class CategoryRepository(BaseRepository):
    def get_by_name(self, name: str) -> CategoryModel | None:
        stmt = self._owner_filter(
            select(CategoryModel).where(CategoryModel.name == name), CategoryModel
        )
        return self.session.scalar(stmt)

    def get_or_create(self, name: str, category_group: str = "geral") -> CategoryModel:
        existing = self.get_by_name(name)
        if existing:
            return existing
        category = CategoryModel(name=name, category_group=category_group, owner_id=self.owner_id)
        self.session.add(category)
        self.session.flush()
        return category

    def list_all(self) -> list[CategoryModel]:
        stmt = self._owner_filter(select(CategoryModel).order_by(CategoryModel.name), CategoryModel)
        return list(self.session.scalars(stmt))

    def delete_by_id(self, category_id: int) -> None:
        category = self.session.get(CategoryModel, category_id)
        if category:
            self.session.delete(category)
            self.session.flush()
