from sqlalchemy import select

from src.models.db_models import CompanyModel, EntityModel
from src.repositories.base import BaseRepository


class CompanyRepository(BaseRepository):
    def get_by_entity_id(self, entity_id: int) -> CompanyModel | None:
        stmt = self._owner_filter(
            select(CompanyModel).where(CompanyModel.entity_id == entity_id), CompanyModel
        )
        return self.session.scalar(stmt)

    def get_by_cnpj(self, cnpj: str) -> CompanyModel | None:
        stmt = self._owner_filter(
            select(CompanyModel).where(CompanyModel.cnpj == cnpj), CompanyModel
        )
        return self.session.scalar(stmt)

    def list_all(self) -> list[CompanyModel]:
        stmt = self._owner_filter(select(CompanyModel).order_by(CompanyModel.cnpj), CompanyModel)
        return list(self.session.scalars(stmt))

    def create(self, entity_id: int, cnpj: str, company_type: str) -> CompanyModel:
        company = CompanyModel(entity_id=entity_id, cnpj=cnpj, company_type=company_type, owner_id=self.owner_id)
        self.session.add(company)
        self.session.flush()
        return company

    def delete_by_id(self, company_id: int) -> None:
        company = self.session.get(CompanyModel, company_id)
        if company:
            self.session.delete(company)
            self.session.flush()

    def list_with_entity(self) -> list[dict]:
        """Retorna empresas com nome da entidade vinculada, ordenadas por nome."""
        stmt = (
            select(CompanyModel, EntityModel)
            .join(EntityModel, CompanyModel.entity_id == EntityModel.id)
            .order_by(EntityModel.name)
        )
        if self.owner_id is not None:
            stmt = stmt.where(CompanyModel.owner_id == self.owner_id)
        rows = self.session.execute(stmt).all()
        return [
            {
                "id": co.id,
                "cnpj": co.cnpj,
                "company_type": co.company_type,
                "entity_id": co.entity_id,
                "nome_empresa": ent.name,
            }
            for co, ent in rows
        ]
