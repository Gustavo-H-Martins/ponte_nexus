from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from src.domain.enums import EntityType, TransactionType


@dataclass(frozen=True)
class Entity:
    name: str
    entity_type: EntityType


@dataclass(frozen=True)
class Account:
    entity_name: str
    account_name: str
    currency: str


@dataclass(frozen=True)
class PfPjRelationship:
    pf_entity_name: str
    pj_entity_name: str


@dataclass(frozen=True)
class Transaction:
    transaction_id: str
    transaction_date: date
    transaction_type: TransactionType
    category: str
    amount: Decimal
    currency: str
    source_account: str
    destination_account: str
    description: str = ""
