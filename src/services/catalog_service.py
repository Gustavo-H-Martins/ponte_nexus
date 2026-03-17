import re
from decimal import Decimal

from src.config.database import SessionLocal
from src.models.db_models import AccountModel, CategoryModel, CompanyModel, EntityModel, IncomeSourceModel
from src.repositories.account_repository import AccountRepository
from src.repositories.category_repository import CategoryRepository
from src.repositories.company_repository import CompanyRepository
from src.repositories.entity_repository import EntityRepository
from src.repositories.income_source_repository import IncomeSourceRepository


def _normalizar_cnpj(cnpj: str) -> str:
    """Remove formatação e retorna 14 dígitos numéricos."""
    return re.sub(r"\D", "", cnpj)


class CatalogService:
    """CRUD de entidades, contas, categorias e empresas.

    Cada método abre e fecha sua própria sessão para isolamento de transações.
    Projetado para suportar, sem refatoração, um futuro módulo administrativo
    multiusuário — bastará injetar um session_factory com escopo de usuário.
    """

    def __init__(self, session_factory=SessionLocal, owner_id: int | None = None) -> None:
        self.session_factory = session_factory
        self.owner_id = owner_id

    # ── Entidades ─────────────────────────────────────────────────────────────

    def list_entities(self, entity_type: str | None = None) -> list[EntityModel]:
        with self.session_factory() as session:
            repo = EntityRepository(session, self.owner_id)
            entities = repo.list_by_type(entity_type) if entity_type else repo.list_all()
            return [_detach_entity(e) for e in entities]

    def create_entity(self, name: str, entity_type: str) -> EntityModel:
        with self.session_factory() as session:
            repo = EntityRepository(session, self.owner_id)
            if repo.get_by_name_and_type(name, entity_type):
                raise ValueError(f"Entidade '{name}' ({entity_type}) já existe.")
            entity = repo.create(name, entity_type)
            session.commit()
            return _detach_entity(entity)

    def delete_entity(self, entity_id: int) -> None:
        with self.session_factory() as session:
            EntityRepository(session, self.owner_id).delete_by_id(entity_id)
            session.commit()

    # ── Contas ────────────────────────────────────────────────────────────────

    def list_accounts(self, entity_id: int | None = None) -> list[AccountModel]:
        with self.session_factory() as session:
            repo = AccountRepository(session, self.owner_id)
            accounts = repo.list_by_entity(entity_id) if entity_id else repo.list_all()
            return [_detach_account(a) for a in accounts]

    def create_account(
        self,
        entity_id: int,
        account_name: str,
        account_type: str = "conta_bancaria",
        currency: str = "BRL",
        description: str | None = None,
    ) -> AccountModel:
        with self.session_factory() as session:
            account = AccountRepository(session, self.owner_id).create(
                account_name=account_name,
                entity_id=entity_id,
                account_type=account_type,
                currency=currency,
                description=description,
            )
            session.commit()
            return _detach_account(account)

    def deactivate_account(self, account_id: int) -> None:
        """Desativa uma conta preservando seu histórico de transações."""
        with self.session_factory() as session:
            AccountRepository(session, self.owner_id).deactivate(account_id)
            session.commit()

    def delete_account(self, account_id: int) -> None:
        with self.session_factory() as session:
            AccountRepository(session, self.owner_id).delete_by_id(account_id)
            session.commit()

    def list_accounts_with_entity(self) -> list[dict]:
        """Retorna todas as contas com dados da entidade vinculada."""
        with self.session_factory() as session:
            return AccountRepository(session, self.owner_id).list_with_entity()

    # ── Categorias ────────────────────────────────────────────────────────────

    def list_categories(self) -> list[CategoryModel]:
        with self.session_factory() as session:
            categories = CategoryRepository(session, self.owner_id).list_all()
            return [_detach_category(c) for c in categories]

    def create_category(self, name: str, category_group: str = "geral") -> CategoryModel:
        with self.session_factory() as session:
            category = CategoryRepository(session, self.owner_id).get_or_create(name, category_group)
            session.commit()
            return _detach_category(category)

    def delete_category(self, category_id: int) -> None:
        with self.session_factory() as session:
            CategoryRepository(session, self.owner_id).delete_by_id(category_id)
            session.commit()

    # ── Empresas (CNPJ) ───────────────────────────────────────────────────────

    def list_companies(self) -> list[dict]:
        """Retorna empresas com nome e tipo da entidade vinculada."""
        with self.session_factory() as session:
            return CompanyRepository(session, self.owner_id).list_with_entity()

    def create_company(
        self, nome_empresa: str, cnpj: str, company_type: str
    ) -> CompanyModel:
        cnpj_clean = _normalizar_cnpj(cnpj)
        if len(cnpj_clean) != 14:
            raise ValueError("CNPJ deve conter 14 dígitos numéricos.")

        with self.session_factory() as session:
            company_repo = CompanyRepository(session, self.owner_id)
            if company_repo.get_by_cnpj(cnpj_clean):
                raise ValueError(f"Empresa com CNPJ {cnpj} já cadastrada.")
            entity = EntityRepository(session, self.owner_id).get_or_create(nome_empresa, "PJ")
            company = company_repo.create(entity.id, cnpj_clean, company_type)
            session.commit()
            return _detach_company(company)

    def delete_company(self, company_id: int) -> None:
        with self.session_factory() as session:
            CompanyRepository(session, self.owner_id).delete_by_id(company_id)
            session.commit()

    # ── Fontes de Renda ───────────────────────────────────────────────────────

    def list_income_sources(self, entity_id: int | None = None) -> list[IncomeSourceModel]:
        """Lista fontes de renda, opcionalmente filtradas por entidade."""
        with self.session_factory() as session:
            repo = IncomeSourceRepository(session, self.owner_id)
            sources = repo.list_by_entity(entity_id) if entity_id else repo.list_active()
            return [_detach_income_source(s) for s in sources]

    def create_income_source(
        self,
        entity_id: int,
        name: str,
        source_type: str,
        expected_monthly_amount: Decimal | None = None,
    ) -> IncomeSourceModel:
        with self.session_factory() as session:
            source = IncomeSourceRepository(session, self.owner_id).create(
                entity_id=entity_id,
                name=name,
                source_type=source_type,
                expected_monthly_amount=expected_monthly_amount,
            )
            session.commit()
            return _detach_income_source(source)

    def deactivate_income_source(self, source_id: int) -> None:
        with self.session_factory() as session:
            IncomeSourceRepository(session, self.owner_id).deactivate(source_id)
            session.commit()


# ── Helpers de materialização (evita DetachedInstanceError) ───────────────────

def _detach_entity(e: EntityModel) -> EntityModel:
    e.id; e.name; e.entity_type  # noqa: E702 — força leitura antes de fechar sessão
    return e


def _detach_account(a: AccountModel) -> AccountModel:
    a.id; a.account_name; a.entity_id; a.currency; a.account_type; a.description; a.is_active  # noqa: E702
    return a


def _detach_category(c: CategoryModel) -> CategoryModel:
    c.id; c.name; c.category_group  # noqa: E702
    return c


def _detach_company(c: CompanyModel) -> CompanyModel:
    c.id; c.cnpj; c.company_type; c.entity_id  # noqa: E702
    return c


def _detach_income_source(s: IncomeSourceModel) -> IncomeSourceModel:
    s.id; s.entity_id; s.name; s.source_type; s.is_active  # noqa: E702
    return s
