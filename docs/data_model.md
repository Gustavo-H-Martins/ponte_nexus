# Modelo de Dados

## Entidades de Domínio

As entidades de domínio em `src/domain/entities.py` são dataclasses imutáveis (`frozen=True`). Representam o modelo conceitual do sistema, independente de banco de dados.

### Entity

Representa uma pessoa física ou jurídica participante de transações.

| Campo | Tipo | Descrição |
|---|---|---|
| `name` | `str` | Nome da entidade |
| `entity_type` | `EntityType` | `PF` ou `PJ` |

### Account

Conta financeira vinculada a uma entidade.

| Campo | Tipo | Descrição |
|---|---|---|
| `entity_name` | `str` | Nome da entidade proprietária |
| `account_name` | `str` | Nome da conta |
| `currency` | `str` | Código da moeda (ex: `BRL`) |

### Transaction

Representa um lançamento financeiro.

| Campo | Tipo | Descrição |
|---|---|---|
| `transaction_id` | `str` | Identificador externo único |
| `transaction_date` | `date` | Data da transação |
| `transaction_type` | `TransactionType` | Tipo do fluxo financeiro |
| `category` | `str` | Categoria do lançamento |
| `amount` | `Decimal` | Valor da transação (sempre positivo) |
| `currency` | `str` | Código da moeda |
| `source_account` | `str` | Conta de origem |
| `destination_account` | `str` | Conta de destino |
| `description` | `str` | Descrição livre (opcional) |

### PfPjRelationship

Vínculo entre uma entidade PF e uma entidade PJ (ex: sócio e empresa).

| Campo | Tipo | Descrição |
|---|---|---|
| `pf_entity_name` | `str` | Nome da entidade PF |
| `pj_entity_name` | `str` | Nome da entidade PJ |

---

## Enums

### EntityType

| Valor | Significado |
|---|---|
| `PF` | Pessoa Física |
| `PJ` | Pessoa Jurídica |

### TransactionType

| Valor | Direção | Descrição |
|---|---|---|
| `receita` | externo → PJ | Receita operacional da empresa |
| `despesa` | PJ → externo | Despesa operacional da empresa |
| `transferencia_pf_pj` | PF → PJ | Transferência entre contas PF e PJ |
| `transferencia_pj_pf` | PJ → PF | Transferência entre contas PJ e PF |
| `aporte_pf_pj` | PF → PJ | Aporte de capital da PF na PJ |
| `emprestimo_pf_pj` | PF → PJ | Empréstimo da PF para a PJ |
| `dividendos` | PJ → PF | Distribuição de lucros para sócios |
| `pro_labore` | PJ → PF | Remuneração pelo trabalho do sócio |

---

## Tabelas do Banco de Dados

O banco é gerenciado pelo SQLAlchemy 2.0. As tabelas são criadas automaticamente via `Base.metadata.create_all()` na inicialização (ambiente dev).

### `entidades`

| Coluna | Tipo | Restrições |
|---|---|---|
| `id` | INTEGER | PK, autoincrement |
| `name` | VARCHAR(255) | NOT NULL |
| `entity_type` | VARCHAR(8) | NOT NULL (`PF` ou `PJ`) |

### `contas`

| Coluna | Tipo | Restrições |
|---|---|---|
| `id` | INTEGER | PK, autoincrement |
| `entity_id` | INTEGER | FK → `entidades.id`, NOT NULL |
| `account_name` | VARCHAR(255) | NOT NULL |
| `currency` | VARCHAR(3) | NOT NULL |

### `categorias`

| Coluna | Tipo | Restrições |
|---|---|---|
| `id` | INTEGER | PK, autoincrement |
| `name` | VARCHAR(255) | NOT NULL |
| `category_group` | VARCHAR(64) | NOT NULL |

### `lancamentos`

| Coluna | Tipo | Restrições |
|---|---|---|
| `id` | INTEGER | PK, autoincrement |
| `external_transaction_id` | VARCHAR(128) | NOT NULL, UNIQUE |
| `transaction_date` | DATE | NOT NULL |
| `transaction_type` | VARCHAR(64) | NOT NULL |
| `description` | TEXT | padrão `""` |
| `amount` | NUMERIC(14,2) | NOT NULL |
| `currency` | VARCHAR(3) | NOT NULL |
| `category_id` | INTEGER | FK → `categorias.id`, NOT NULL |
| `source_account_id` | INTEGER | FK → `contas.id`, NOT NULL |
| `destination_account_id` | INTEGER | FK → `contas.id`, NOT NULL |
| `source_entity_id` | INTEGER | FK → `entidades.id`, NOT NULL |
| `destination_entity_id` | INTEGER | FK → `entidades.id`, NOT NULL |
| `created_at` | DATETIME | NOT NULL, server default now() |

**Nota:** `external_transaction_id` corresponde ao campo `id_lancamento` do arquivo importado. A constraint UNIQUE garante idempotência na ingestão — registros duplicados são ignorados sem erro.

### `relacionamentos_pf_pj`

| Coluna | Tipo | Restrições |
|---|---|---|
| `id` | INTEGER | PK, autoincrement |
| `pf_entity_id` | INTEGER | FK → `entidades.id`, NOT NULL |
| `pj_entity_id` | INTEGER | FK → `entidades.id`, NOT NULL |
| `created_at` | DATETIME | NOT NULL, server default now() |

---

## Diagrama de Relacionamentos

```
entidades ──< contas
entidades ──< lancamentos (source_entity_id)
entidades ──< lancamentos (destination_entity_id)
contas    ──< lancamentos (source_account_id)
contas    ──< lancamentos (destination_account_id)
categorias──< lancamentos
entidades ──< relacionamentos_pf_pj (pf_entity_id)
entidades ──< relacionamentos_pf_pj (pj_entity_id)
```

---

## Regras de Negócio

Definidas em `src/domain/rules.py`:

- Transações `transferencia_pf_pj`, `aporte_pf_pj` e `emprestimo_pf_pj` exigem `source_entity_type = PF` e `destination_entity_type = PJ`.
- Transações `transferencia_pj_pf`, `dividendos` e `pro_labore` exigem `source_entity_type = PJ` e `destination_entity_type = PF`.
- `receita` e `despesa` não possuem restrição de direção PF/PJ.
