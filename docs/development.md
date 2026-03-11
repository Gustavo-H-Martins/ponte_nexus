# Guia do Desenvolvedor

## Configuração do Ambiente

**Pré-requisitos:** Python 3.12, Git.

```bash
# 1. Clone o repositório
git clone <url-do-repositorio>
cd ponte_nexus

# 2. Crie o ambiente virtual
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure variáveis de ambiente
cp .env.example .env
# Edite .env se necessário
```

---

## Execução Local

```bash
streamlit run app/streamlit_app.py
```

O banco SQLite é criado automaticamente em `data/ponte_nexus.db` na primeira execução.

Para limpar o banco e recomeçar:

```bash
del data\ponte_nexus.db    # Windows
rm data/ponte_nexus.db     # Linux / macOS
```

---

## Testes

```bash
# Todos os testes
python -m pytest tests/ -v

# Apenas testes unitários
python -m pytest tests/unit/ -v

# Apenas testes de integração
python -m pytest tests/integration/ -v
```

Os testes de integração usam banco SQLite em memória configurado em `tests/conftest.py`. Não há dependência de banco externo.

---

## Estrutura do Novo Scaffold

Todo trabalho novo deve ser direcionado ao scaffold em `app/` + `src/`. O scaffold legado em `pages/` + `src/fin_dashboard/` está preservado e **não deve ser alterado** até a migração estar completa.

```
app/          → UI (Streamlit)
src/
  config/     → settings e database engine
  domain/     → entidades, enums, regras (sem infra)
  models/     → ORM SQLAlchemy
  repositories/ → acesso ao banco
  services/   → orquestração
  ingestion/  → pipeline de leitura e validação
  validation/ → schemas Pydantic
  analytics/  → funções puras de cálculo
```

---

## Como Adicionar uma Nova Página

1. Crie o arquivo em `app/pages/` seguindo a convenção `NN_nome_da_pagina.py`.
2. A página **não deve** conter lógica de negócio — apenas chamadas a serviços/analytics e renderização.
3. Carregue dados com `@st.cache_data(ttl=30)`.
4. Use `page_header()` de `app/ui.py` para manter o layout consistente.

Exemplo mínimo:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st
from src.analytics.loader import load_transactions_df
from app.ui import page_header, plotly_layout

st.set_page_config(page_title="Minha Página · Ponte Nexus", layout="wide", page_icon="💠")

@st.cache_data(ttl=30)
def _get_data():
    return load_transactions_df()

is_dark = page_header("Minha Página", "Subtítulo da página")
LAYOUT = plotly_layout(is_dark)
df = _get_data()
```

---

## Como Adicionar um Novo Tipo de Transação

1. Adicione o novo valor ao enum `TransactionType` em `src/domain/enums.py`.
2. Se houver restrição de direção PF↔PJ, atualize `validate_flow_direction()` em `src/domain/rules.py`.
3. Adicione o mapeamento de label legível em `TIPO_LABEL` em `app/ui.py`.
4. Adicione a cor correspondente em `TYPE_COLORS` em `app/ui.py`.
5. Atualize os testes em `tests/unit/` e `tests/integration/`.

---

## Como Adicionar um Novo Reader de Arquivo

1. Crie o reader em `src/ingestion/readers/novo_reader.py`.
2. A função deve aceitar `str | IO` e retornar `pd.DataFrame`.
3. Registre a extensão em `src/ingestion/parser.py`.
4. Importe e use o reader em `src/ingestion/pipeline.py`.

---

## Convenções de Código

**Tipagem:** annotations de tipo obrigatórias em todas as assinaturas. Evite `Any`.

**Pydantic v2:** use `model_config = ConfigDict(...)` — não o inner class `Config` legado.

**SQLAlchemy 2.0:** use `Mapped[T]` e `mapped_column()` em todos os modelos. Sessões gerenciadas com context manager.

**Pandas:** declare dtypes explícitos ao ler arquivos. Funções de analytics são puras — recebem e retornam DataFrames sem efeitos colaterais.

**Injeção de dependências:** repositórios e serviços recebem dependências pelo construtor. Nunca instancie infraestrutura dentro de lógica de negócio.

**Docstrings:** obrigatórias apenas para funções públicas com lógica não-óbvia. Em português brasileiro. Explique o *porquê*, não o *o quê*.

---

## Segurança

- Todo dado externo (arquivos importados, entrada do usuário) passa por validação Pydantic antes de qualquer processamento.
- Todas as queries usam SQLAlchemy ORM ou `select()` parametrizado. Nunca interpole input de usuário em strings SQL.
- Credenciais pertencem ao `.env`. Nunca commite `.env`.
- Não logue dados financeiros sensíveis.

---

## Variáveis de Ambiente

| Variável | Padrão | Descrição |
|---|---|---|
| `DATABASE_URL` | `sqlite:///data/ponte_nexus.db` | URL de conexão com o banco |
| `APP_NAME` | `Ponte Nexus` | Nome da aplicação |

---

## Migrações de Schema

Ainda não há Alembic configurado. Qualquer alteração em `src/models/db_models.py` que mude o schema requer atenção — o `Base.metadata.create_all()` não altera tabelas existentes. Para ambientes com dados persistidos, será necessário criar a migração manualmente ou configurar Alembic (ver [roadmap](roadmap.md)).
