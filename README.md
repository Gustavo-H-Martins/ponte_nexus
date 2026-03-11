# Ponte Nexus

Dashboard financeiro para análise de fluxos entre **Pessoa Física (PF)** e **Pessoa Jurídica (PJ)** no contexto tributário brasileiro. Permite importar lançamentos financeiros (CSV, XLSX ou JSON), validar os dados e visualizar indicadores consolidados em tempo real.

---

## O problema que resolve

Sócios e profissionais que operam PF e PJ simultaneamente precisam enxergar como o dinheiro transita entre as duas esferas — aportes, pró-labore, dividendos, empréstimos — em um único painel, sem depender de planilhas manuais ou ferramentas de contabilidade complexas.

---

## Visão geral da arquitetura

```
Streamlit UI (app/pages/)
    │
    ▼
Services (src/services/)
    ├── IngestionPipeline (src/ingestion/)
    │       ├── Readers: CSV · XLSX · JSON
    │       ├── Normalizer
    │       └── Validator (Pydantic v2)
    └── Repositories (src/repositories/)
            │
            ▼
        SQLAlchemy ORM (src/models/)
            │
            ▼
        SQLite (dev) / PostgreSQL (produção)
```

Regras de domínio em `src/domain/rules.py` são chamadas pela camada de serviço — nunca pela UI nem pelos repositórios.

---

## Tecnologias

| Camada | Tecnologia |
|---|---|
| Interface | Python 3.12 · Streamlit ≥ 1.40 |
| Visualização | Plotly ≥ 5.24 |
| Validação | Pydantic v2 · pydantic-settings |
| Persistência | SQLAlchemy 2.0 · SQLite (dev) · PostgreSQL (prod) |
| Análise | pandas ≥ 2.2 |
| Exportação | openpyxl · fpdf2 |

---

## Instalação

**Pré-requisitos:** Python 3.12, pip ou pipenv.

```bash
# 1. Clone o repositório
git clone <url-do-repositorio>
cd ponte_nexus

# 2. Crie o ambiente virtual e instale as dependências
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux / macOS

pip install -r requirements.txt

# 3. Configure as variáveis de ambiente
cp .env.example .env
# Edite .env se necessário (o padrão usa SQLite local)
```

---

## Execução

```bash
streamlit run app/streamlit_app.py
```

O banco de dados SQLite é criado automaticamente em `data/ponte_nexus.db` na primeira execução.

Para usar PostgreSQL em produção, defina `DATABASE_URL` no `.env`:

```
DATABASE_URL=postgresql://user:password@host:5432/ponte_nexus
```

---

## Exemplo de uso

1. Acesse a página **Importação de Dados** no menu lateral.
2. Faça upload de um arquivo CSV, XLSX ou JSON seguindo o schema abaixo.
3. O sistema valida os dados e persiste os registros válidos.
4. Navegue pelas páginas analíticas para visualizar os indicadores.

Um arquivo de exemplo está disponível em `data/samples/sample_valid.csv`.

**Colunas obrigatórias:**

| Coluna | Formato | Descrição |
|---|---|---|
| `id_lancamento` | texto | Identificador único do lançamento |
| `data` | YYYY-MM-DD | Data da transação |
| `tipo_entidade` | `PF` ou `PJ` | Tipo da entidade principal |
| `nome_entidade` | texto | Nome da entidade principal |
| `tipo_transacao` | ver abaixo | Tipo do fluxo financeiro |
| `categoria` | texto | Categoria do lançamento |
| `descricao` | texto | Descrição livre |
| `valor` | decimal > 0 | Valor da transação |
| `moeda` | 3 letras | Código da moeda (ex: `BRL`) |
| `conta_origem` | texto | Conta de origem |
| `conta_destino` | texto | Conta de destino |

Coluna opcional: `nome_contraparte` — entidade de contraparte em fluxos cruzados PF↔PJ.

**Tipos de transação válidos:**

`receita` · `despesa` · `transferencia_pf_pj` · `transferencia_pj_pf` · `aporte_pf_pj` · `emprestimo_pf_pj` · `dividendos` · `pro_labore`

---

## Testes

```bash
python -m pytest tests/ -v
```

---

## Estrutura do projeto

```
app/
  streamlit_app.py        Entry point da aplicação
  pages/                  Páginas do dashboard (Streamlit multipage)
  ui.py                   Utilitários de UI compartilhados
  export.py               Exportação para PDF e Excel
src/
  config/                 Settings (pydantic-settings) e engine SQLAlchemy
  domain/                 Entidades, enums e regras de negócio (sem dependências de infra)
  models/                 Modelos ORM SQLAlchemy
  repositories/           Acesso ao banco de dados
  services/               Orquestração: ingestão e persistência
  ingestion/              Pipeline de leitura, normalização e validação de arquivos
  validation/             Schemas Pydantic e validadores
  analytics/              Funções puras de cálculo (KPIs, fluxo PF/PJ, loader SQL)
data/
  samples/                Arquivos de exemplo para importação
tests/
  unit/                   Testes de validação e regras de domínio
  integration/            Testes de pipeline e serviço de ingestão
docs/
  architecture.md         Arquitetura detalhada do sistema
  data_model.md           Modelo de dados e entidades
  data_ingestion.md       Formato dos arquivos de importação
  dashboard.md            Páginas e indicadores do painel
  development.md          Guia do desenvolvedor
  roadmap.md              Evoluções planejadas
  decisions/              Registros de decisão arquitetural (ADR)
```

---

## Documentação

- [Arquitetura](docs/architecture.md)
- [Modelo de dados](docs/data_model.md)
- [Ingestão de dados](docs/data_ingestion.md)
- [Dashboard](docs/dashboard.md)
- [Desenvolvimento](docs/development.md)
- [Roadmap](docs/roadmap.md)
