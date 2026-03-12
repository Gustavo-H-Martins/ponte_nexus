from sqlalchemy import select

from src.models.db_models import CompanyModel
from src.repositories.base import BaseRepository


class CompanyRepository(BaseRepository):
    def get_by_entity_id(self, entity_id: int) -> CompanyModel | None:
        stmt = select(CompanyModel).where(CompanyModel.entity_id == entity_id)
        return self.session.scalar(stmt)

    def get_by_cnpj(self, cnpj: str) -> CompanyModel | None:
        stmt = select(CompanyModel).where(CompanyModel.cnpj == cnpj)
        return self.session.scalar(stmt)

    def list_all(self) -> list[CompanyModel]:
        stmt = select(CompanyModel).order_by(CompanyModel.cnpj)
        return list(self.session.scalars(stmt))

    def create(self, entity_id: int, cnpj: str, company_type: str) -> CompanyModel:
        company = CompanyModel(entity_id=entity_id, cnpj=cnpj, company_type=company_type)
        self.session.add(company)
        self.session.flush()
        return company

    def delete_by_id(self, company_id: int) -> None:
        company = self.session.get(CompanyModel, company_id)
        if company:
            self.session.delete(company)
            self.session.flush()
