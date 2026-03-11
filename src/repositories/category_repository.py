from sqlalchemy import select

from src.models.db_models import CategoryModel
from src.repositories.base import BaseRepository


class CategoryRepository(BaseRepository):
    def get_by_name(self, name: str) -> CategoryModel | None:
        stmt = select(CategoryModel).where(CategoryModel.name == name)
        return self.session.scalar(stmt)

    def get_or_create(self, name: str, category_group: str = "geral") -> CategoryModel:
        existing = self.get_by_name(name)
        if existing:
            return existing
        category = CategoryModel(name=name, category_group=category_group)
        self.session.add(category)
        self.session.flush()
        return category
