# Ponte Nexus

Painel de analise financeira para Pessoa Fisica (PF) e Pessoa Juridica (PJ) com ingestao de dados (CSV, XLSX, JSON), validacao de schema e visualizacao em Streamlit.

## Executar a aplicacao

```bash
streamlit run app/streamlit_app.py
```

O banco de dados SQLite e criado automaticamente em `data/ponte_nexus.db` na primeira execucao.

## Importar dados

Use a pagina **Importacao de Dados** para carregar arquivos CSV, XLSX ou JSON.

Um arquivo de exemplo esta disponivel em `data/samples/sample_valid.csv`.

Colunas obrigatorias:

| Coluna | Formato |
|---|---|
| transaction_id | texto unico |
| date | YYYY-MM-DD |
| entity_type | PF ou PJ |
| entity_name | texto |
| transaction_type | ver tipos abaixo |
| category | texto |
| description | texto |
| amount | decimal > 0 |
| currency | 3 letras (ex: BRL) |
| source_account | texto |
| destination_account | texto |

Coluna opcional: `counter_entity_name` (entidade de contraparte em fluxos cruzados PF<->PJ).

Tipos de transacao: `income`, `expense`, `transfer_pf_to_pj`, `transfer_pj_to_pf`, `investment_pf_to_pj`, `loan_pf_to_pj`, `dividend_distribution`, `pro_labore`

## Configuracao

Copie `.env.example` para `.env` e ajuste conforme necessario:

```bash
cp .env.example .env
```

Para usar PostgreSQL em producao, defina `DATABASE_URL` no `.env`:

```
DATABASE_URL=postgresql://user:password@host:5432/ponte_nexus
```

## Executar testes

```bash
python -m pytest tests/ -v
```

## Estrutura do projeto

```
app/                    Entry point e paginas Streamlit
src/
  config/               Settings (pydantic-settings) e engine SQLAlchemy
  domain/               Entidades, enums e regras de negocio (sem dependencias de infra)
  models/               Modelos ORM SQLAlchemy
  repositories/         Acesso ao banco de dados
  services/             Orquestracao: ingestao com persistencia
  ingestion/            Pipeline de leitura, normalizacao e validacao de arquivos
  validation/           Schemas Pydantic e validadores
  analytics/            Funcoes puras de calculo (KPIs, fluxo PF/PJ, loader SQL)
data/
  samples/              Arquivos de exemplo para teste de importacao
tests/
  unit/                 Testes de validacao e regras de dominio
  integration/          Testes de pipeline e servico de ingestao
```

## Stack

- Python 3.12
- Streamlit >= 1.40
- pandas >= 2.2
- Pydantic v2 + pydantic-settings
- SQLAlchemy 2.0
- Plotly >= 5.24
- SQLite (dev) / PostgreSQL (producao)
