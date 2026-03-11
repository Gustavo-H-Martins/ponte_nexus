# Arquitetura do Sistema

## Visão Geral

O Ponte Nexus é estruturado em camadas com separação clara de responsabilidades. A UI em Streamlit não contém lógica de negócio — ela apenas chama serviços e renderiza resultados.

---

## Diagrama de Camadas

```
┌─────────────────────────────────────────────┐
│               Streamlit UI                  │
│           app/pages/*.py                    │
│  Renderização, filtros, upload de arquivos  │
└──────────────────┬──────────────────────────┘
                   │ chama
┌──────────────────▼──────────────────────────┐
│               Services                      │
│           src/services/                     │
│  Orquestração: ingestão + persistência      │
│  IngestionService · AnalyticsService        │
└──────┬────────────────────────┬─────────────┘
       │ usa                    │ usa
┌──────▼──────────┐   ┌─────────▼─────────────┐
│  IngestionPipe  │   │    Repositories        │
│  src/ingestion/ │   │  src/repositories/     │
│  Reader         │   │  EntityRepository      │
│  Normalizer     │   │  AccountRepository     │
│  Validator      │   │  CategoryRepository    │
└──────┬──────────┘   │  TransactionRepository │
       │ valida com   └─────────┬──────────────┘
┌──────▼──────────┐             │ usa
│   Validation    │   ┌─────────▼──────────────┐
│  src/validation/│   │   SQLAlchemy ORM        │
│  Pydantic v2    │   │   src/models/           │
└─────────────────┘   └─────────┬──────────────┘
                                 │ persiste em
                      ┌──────────▼─────────────┐
                      │      Banco de Dados     │
                      │  SQLite (dev)           │
                      │  PostgreSQL (produção)  │
                      └────────────────────────┘

          Analytics (src/analytics/)
          ──────────────────────────
          Funções puras que recebem
          DataFrames e retornam
          resultados calculados.
          Sem acesso direto ao banco.
```

---

## Camadas da Aplicação

### UI — `app/`

- **`streamlit_app.py`**: entry point, inicializa o banco de dados e renderiza a página inicial.
- **`pages/`**: cada arquivo é uma página do dashboard multipage do Streamlit.
- **`ui.py`**: funções de layout compartilhadas (`page_header`, `plotly_layout`, mapeamento de cores e labels).
- **`export.py`**: geração de arquivos PDF e Excel para download.

A UI não instancia repositórios nem acessa o banco diretamente. Para operações de leitura, ela usa `src/analytics/loader.py`. Para ingestão, usa `src/services/ingestion_service.py`.

### Services — `src/services/`

Orquestradores que coordenam o pipeline de ingestão com a persistência:

- **`IngestionService`**: recebe um arquivo (path ou bytes), executa o `IngestionPipeline` e persiste os registros válidos via repositórios.
- **`AnalyticsService`**: (em desenvolvimento) agregará lógica de consulta analítica.
- **`TransactionService`**: (em desenvolvimento) operações sobre lançamentos individuais.

### Ingestion — `src/ingestion/`

Pipeline responsável por transformar arquivos brutos em DataFrames válidos:

1. **`parser.py`**: detecta o formato do arquivo pela extensão.
2. **`readers/`**: lê CSV, XLSX ou JSON e retorna um `pd.DataFrame`.
3. **`normalizer.py`**: normaliza nomes de colunas e valores de enums (case-insensitive).
4. **`pipeline.py`**: orquestra os passos acima e retorna o resultado com estatísticas.

### Validation — `src/validation/`

- **`schemas.py`**: schema Pydantic v2 (`TransactionImportSchema`) com todas as regras de campo.
- **`validators.py`**: itera o DataFrame linha a linha, aplica o schema e coleta erros.
- **`error_report.py`**: formata a lista de erros para exibição na UI.

### Domain — `src/domain/`

Núcleo do sistema, sem dependências de infraestrutura:

- **`entities.py`**: dataclasses imutáveis (`frozen=True`) — `Entity`, `Account`, `Transaction`, `PfPjRelationship`.
- **`enums.py`**: `EntityType` (PF/PJ) e `TransactionType` (8 tipos de fluxo).
- **`rules.py`**: `validate_flow_direction()` — garante que a direção do fluxo PF↔PJ é compatível com o tipo de transação.

### Repositories — `src/repositories/`

Acesso ao banco via SQLAlchemy 2.0. Cada repositório recebe uma `Session` por injeção de construtor:

- `EntityRepository` — entidades (PF/PJ)
- `AccountRepository` — contas vinculadas a entidades
- `CategoryRepository` — categorias de lançamento
- `TransactionRepository` — lançamentos financeiros
- `PfPjRelationshipRepository` — vínculos PF↔PJ

### Models — `src/models/`

Modelos ORM com `Mapped[T]` e `mapped_column()` (SQLAlchemy 2.0). Tabelas: `entidades`, `contas`, `categorias`, `lancamentos`, `relacionamentos_pf_pj`.

### Analytics — `src/analytics/`

Funções puras que recebem DataFrames e retornam DataFrames ou dicionários calculados. Não produzem efeitos colaterais.

- **`loader.py`**: carrega lançamentos do banco como DataFrame via SQL.
- **`kpis.py`**: `pf_pj_kpis()`, `monthly_net_result()`, `revenue_expense_by_month()`.
- **`cashflow.py`**: `pf_pj_flow()` — filtra transações de fluxo cruzado.
- **`pf_pj_analysis.py`**: `summarize_pf_pj_direction()` — sumariza direção do fluxo.

---

## Fluxo de Dados: Ingestão

```
Arquivo (CSV/XLSX/JSON)
        │
        ▼
    Reader          → pd.DataFrame bruto
        │
        ▼
    Normalizer      → normaliza colunas e enums
        │
        ▼
    Validator       → valida schema linha a linha (Pydantic)
        │
   ┌────┴────┐
 falhou    passou
   │          │
   ▼          ▼
ErrorReport  IngestionService
             │
             ├── EntityRepository       → upsert entidades
             ├── AccountRepository      → upsert contas
             ├── CategoryRepository     → upsert categorias
             └── TransactionRepository  → insert (skip duplicatas)
```

---

## Fluxo de Dados: Visualização

```
Streamlit page
    │
    ▼
@st.cache_data
    │
    ▼
analytics/loader.py  →  SQL → banco → pd.DataFrame
    │
    ▼
analytics/kpis.py | cashflow.py | pf_pj_analysis.py
    │
    ▼
Plotly charts / st.metric / st.dataframe
```

---

## Configuração

`src/config/settings.py` usa `pydantic-settings` para ler variáveis de ambiente do `.env`. O padrão é SQLite local. `src/config/database.py` gerencia a engine SQLAlchemy e o `SessionLocal`.

---

## Decisões de Arquitetura

- [ADR-001 — Escolha do Streamlit](decisions/001-streamlit-choice.md)
