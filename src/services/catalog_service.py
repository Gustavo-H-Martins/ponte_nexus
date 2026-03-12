import re

from src.config.database import SessionLocal
from src.models.db_models import AccountModel, CategoryModel, CompanyModel, EntityModel
from src.repositories.account_repository import AccountRepository
from src.repositories.category_repository import CategoryRepository
from src.repositories.company_repository import CompanyRepository
from src.repositories.entity_repository import EntityRepository


def _normalizar_cnpj(cnpj: str) -> str:
    """Remove formatação e retorna 14 dígitos numéricos."""
    return re.sub(r"\D", "", cnpj)


class CatalogService:
    """CRUD de entidades, contas, categorias e empresas.

    Cada método abre e fecha sua própria sessão para isolamento de transações.
    Projetado para suportar, sem refatoração, um futuro módulo administrativo
    multiusuário — bastará injetar um session_factory com escopo de usuário.
    """

    def __init__(self, session_factory=SessionLocal) -> None:
        self.session_factory = session_factory

    # ── Entidades ─────────────────────────────────────────────────────────────

    def list_entities(self, entity_type: str | None = None) -> list[EntityModel]:
        with self.session_factory() as session:
            repo = EntityRepository(session)
            entities = repo.list_by_type(entity_type) if entity_type else repo.list_all()
            # Materializa atributos escalares antes de fechar a sessão
            return [_detach_entity(e) for e in entities]

    def create_entity(self, name: str, entity_type: str) -> EntityModel:
        with self.session_factory() as session:
            repo = EntityRepository(session)
            if repo.get_by_name_and_type(name, entity_type):
                raise ValueError(f"Entidade '{name}' ({entity_type}) já existe.")
            entity = repo.create(name, entity_type)
            session.commit()
            return _detach_entity(entity)

    def delete_entity(self, entity_id: int) -> None:
        with self.session_factory() as session:
            EntityRepository(session).delete_by_id(entity_id)
            session.commit()

    # ── Contas ────────────────────────────────────────────────────────────────

    def list_accounts(self, entity_id: int | None = None) -> list[AccountModel]:
        with self.session_factory() as session:
            repo = AccountRepository(session)
            accounts = repo.list_by_entity(entity_id) if entity_id else repo.list_all()
            return [_detach_account(a) for a in accounts]

    def create_account(
        self, entity_id: int, account_name: str, currency: str = "BRL"
    ) -> AccountModel:
        with self.session_factory() as session:
            account = AccountRepository(session).get_or_create(
                account_name, entity_id, currency
            )
            session.commit()
            return _detach_account(account)

    def delete_account(self, account_id: int) -> None:
        with self.session_factory() as session:
            AccountRepository(session).delete_by_id(account_id)
            session.commit()

    # ── Categorias ────────────────────────────────────────────────────────────

    def list_categories(self) -> list[CategoryModel]:
        with self.session_factory() as session:
            categories = CategoryRepository(session).list_all()
            return [_detach_category(c) for c in categories]

    def create_category(self, name: str, category_group: str = "geral") -> CategoryModel:
        with self.session_factory() as session:
            category = CategoryRepository(session).get_or_create(name, category_group)
            session.commit()
            return _detach_category(category)

    def delete_category(self, category_id: int) -> None:
        with self.session_factory() as session:
            CategoryRepository(session).delete_by_id(category_id)
            session.commit()

    # ── Empresas (CNPJ) ───────────────────────────────────────────────────────

    def list_companies(self) -> list[dict]:
        """Retorna empresas com nome e tipo da entidade vinculada."""
        from sqlalchemy import select, text

        from src.config.database import engine

        with engine.connect() as conn:
            rows = conn.execute(
                text(
                    "SELECT c.id, c.cnpj, c.company_type, c.entity_id, e.name AS nome_empresa "
                    "FROM empresas c JOIN entidades e ON e.id = c.entity_id "
                    "ORDER BY e.name"
                )
            ).mappings().all()
            return [dict(r) for r in rows]

    def create_company(
        self, nome_empresa: str, cnpj: str, company_type: str
    ) -> CompanyModel:
        cnpj_clean = _normalizar_cnpj(cnpj)
        if len(cnpj_clean) != 14:
            raise ValueError("CNPJ deve conter 14 dígitos numéricos.")

        with self.session_factory() as session:
            company_repo = CompanyRepository(session)
            if company_repo.get_by_cnpj(cnpj_clean):
                raise ValueError(f"Empresa com CNPJ {cnpj} já cadastrada.")
            entity = EntityRepository(session).get_or_create(nome_empresa, "PJ")
            company = company_repo.create(entity.id, cnpj_clean, company_type)
            session.commit()
            return _detach_company(company)

    def delete_company(self, company_id: int) -> None:
        with self.session_factory() as session:
            CompanyRepository(session).delete_by_id(company_id)
            session.commit()


# ── Helpers de materialização (evita DetachedInstanceError) ───────────────────

def _detach_entity(e: EntityModel) -> EntityModel:
    e.id; e.name; e.entity_type  # noqa: E702 — força leitura antes de fechar sessão
    return e


def _detach_account(a: AccountModel) -> AccountModel:
    a.id; a.account_name; a.entity_id; a.currency  # noqa: E702
    return a


def _detach_category(c: CategoryModel) -> CategoryModel:
    c.id; c.name; c.category_group  # noqa: E702
    return c


def _detach_company(c: CompanyModel) -> CompanyModel:
    c.id; c.cnpj; c.company_type; c.entity_id  # noqa: E702
    return c
