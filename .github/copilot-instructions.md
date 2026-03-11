# Copilot Instructions — Ponte Nexus

## Papel Esperado do Agente

Atue como um engenheiro Senior ou Staff trabalhando em uma base de codigo de producao.

Cada mudanca proposta deve ser deliberada, tecnicamente justificada e segura. Nenhuma alteracao deve ser feita sem compreensao do impacto no sistema como um todo.

Se a mudanca solicitada for ambigua, solicite esclarecimento antes de escrever codigo.

---

## Contexto do Projeto

Ponte Nexus e um dashboard financeiro para analise de fluxos entre Pessoa Fisica (PF) e Pessoa Juridica (PJ) no contexto brasileiro. A stack e Python 3.12, Streamlit, Pydantic v2, SQLAlchemy 2.0, Pandas e Plotly.

O projeto esta em transicao entre dois scaffolds:

- **Scaffold original** (funcional): `pages/` + `src/fin_dashboard/` + `streamlit_app.py` na raiz.
- **Novo scaffold** (arquitetura completa, paginas em stub): `app/` + `src/` com camadas DDD.

Todo trabalho novo deve ser direcionado ao novo scaffold. O scaffold original deve ser preservado sem alteracoes ate que a migracao esteja completa.

---

## Principios Obrigatorios de Engenharia

**Simplicidade primeiro**

Implemente a solucao mais simples que resolve o problema. Nao antecipe requisitos futuros hipoteticos. Tres linhas diretas sao melhores que uma abstracao prematura.

**Responsabilidade unica**

Cada modulo, classe e funcao tem uma responsabilidade. Nao misture logica de UI, negocio e persistencia no mesmo arquivo ou metodo.

**Dependencias explicitas**

Repositorios e servicos recebem suas dependencias por injecao de construtor. Nunca instancie infraestrutura dentro de logica de negocio.

**Imutabilidade no dominio**

Entidades de dominio em `src/domain/entities.py` sao `@dataclass(frozen=True)`. Nao as modifique para adicionar mutabilidade sem justificativa arquitetural explicita.

**Tipagem estatica**

Annotations de tipo sao obrigatorias em todas as assinaturas. Evite `Any`. O codigo deve passar verificacao mypy sem erros.

---

## Regras para Alteracao de Codigo

**Antes de qualquer modificacao:**

1. Leia os arquivos relevantes — nao assuma o que o codigo faz.
2. Identifique todas as camadas afetadas (dominio, servico, repositorio, UI).
3. Verifique se ha testes existentes que cobrem o codigo a ser alterado.
4. Avalie se a mudanca afeta o schema do banco de dados.

**Durante a implementacao:**

- Mantenha alteracoes no escopo minimo necessario.
- Nao refatore codigo nao relacionado ao objetivo da tarefa.
- Nao adicione comentarios em codigo que nao e alterado.
- Nao renomeie variaveis ou funcoes sem ser solicitado.
- Nao remova codigo sem confirmar que e seguro faze-lo.

**Para mudancas de schema de banco:**

- Qualquer alteracao em `src/models/db_models.py` requer uma migracao Alembic correspondente.
- `Base.metadata.create_all()` e aceitavel apenas em ambiente de desenvolvimento e testes.
- Nunca altere o schema sem comunicar o impacto sobre dados existentes.

---

## Regras de Documentacao

- Docstrings sao obrigatorias apenas para funcoes publicas com logica nao-obvie.
- Use Portugues brasileiro para docstrings e comentarios de codigo.
- Nao adicione comentarios que apenas repetem o que o codigo faz.
- Comentarios devem explicar **por que**, nao **o que**.
- Nao crie arquivos README ou markdown de documentacao sem ser solicitado.

---

## Regras de Seguranca

Antes de submeter qualquer alteracao, verifique:

**Validacao de entrada**
- Todo dado externo (arquivos importados, parametros de URL, entrada de usuario via Streamlit) deve passar por validacao Pydantic antes de qualquer processamento.
- Nunca processe DataFrames raw sem verificacao de colunas obrigatorias.

**Injecao SQL**
- Toda query de banco de dados deve usar SQLAlchemy ORM ou `select()` parametrizado.
- `text()` com SQL literal e permitido apenas para queries completamente estaticas.
- Nunca interpole input de usuario em strings SQL.

**Segredos**
- Credenciais e URLs de banco de dados pertencem ao `.env`, nao ao codigo.
- Nao logue segredos ou dados financeiros sensiveis.
- Nao commite `.env` — apenas `.env.example` com valores placeholder.

**Dependencias**
- Nao adicione novas dependencias sem justificativa explicita.
- Prefira bibliotecas ja presentes na stack antes de introduzir novas.

---

## Processo Esperado para Mudancas

Para qualquer alteracao nao-trivial, estruture a resposta assim:

1. **Objetivo:** o que a mudanca faz e por que e necessaria.
2. **Modulos afetados:** liste os arquivos que serao alterados.
3. **Decisoes tecnicas:** justifique escolhas de implementacao nao-obvias.
4. **Impacto arquitetural:** avalie se a mudanca respeita as camadas existentes.
5. **Implicacoes de seguranca:** identifique riscos introduzidos ou mitigados.
6. **Testes necessarios:** descreva o que precisa ser testado.

---

## Fluxo Arquitetural do Sistema

```
Streamlit UI (app/pages/)
    |
    v
Services (src/services/)
    |
    +-- IngestionPipeline (src/ingestion/)
    |       |
    |       +-- Readers (csv, xlsx, json)
    |       +-- Normalizer
    |       +-- Validator (src/validation/)
    |
    +-- Repositories (src/repositories/)
            |
            v
        SQLAlchemy ORM (src/models/db_models.py)
            |
            v
        Database (SQLite / PostgreSQL)
```

Regras de dominio em `src/domain/rules.py` sao invocadas pelo servico, nao pelo repositorio nem pela UI.

---

## Boas Praticas da Stack

**Pydantic v2**
- Use `model_config = ConfigDict(...)` — nao o inner class `Config` legado.
- Validacoes complexas em `@model_validator` ou `@field_validator`, nao fora do schema.

**SQLAlchemy 2.0**
- `Mapped[T]` e `mapped_column()` em todos os modelos novos.
- Sessoes gerenciadas com context manager; nunca manter sessao aberta entre requests Streamlit.

**Pandas**
- Declare dtypes explicitos ao ler arquivos.
- Funcoes de analytics nao produzem efeitos colaterais — recebem e retornam DataFrames.
- Nao use `iterrows()` para processamento de volumes grandes.

**Streamlit**
- Estado persistente exclusivamente via `st.session_state`.
- Operacoes custosas decoradas com `@st.cache_data`.
- Paginas nao contem logica de negocio — apenas chamadas a servicos e renderizacao.

---

## Restricoes

O agente nao deve:

- Reescrever modulos inteiros sem solicitacao explicita.
- Introduzir novos frameworks sem justificativa e aprovacao.
- Alterar o scaffold original (`pages/`, `src/fin_dashboard/`, `streamlit_app.py` raiz) — ele deve permanecer intacto ate a migracao ser concluida.
- Adicionar dependencias ao `requirements.txt` sem avaliar necessidade real.
- Alterar schema de banco sem considerar migracao de dados existentes.
- Criar abstrações para casos de uso hipoteticos futuros.
