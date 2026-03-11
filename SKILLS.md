# SKILLS.md — Ponte Nexus

## 1. Visao Geral Tecnica

Ponte Nexus e um dashboard de analise financeira pessoal para o contexto brasileiro de Pessoa Fisica (PF) e Pessoa Juridica (PJ). O sistema permite importacao de dados financeiros a partir de arquivos CSV, XLSX e JSON, aplica um pipeline de validacao e normalizacao, persiste os dados em um banco relacional e exibe analises e KPIs via interface Streamlit.

O projeto esta em transicao entre dois scaffolds:

- **Scaffold original** (`pages/` + `src/fin_dashboard/`): funcional, conectado ao entry point `streamlit_app.py` na raiz.
- **Novo scaffold** (`app/` + camadas refatoradas em `src/`): arquitetura completa com DDD, repositorios tipados e schema de banco normalizado, mas com paginas ainda em stub.

Qualquer trabalho novo deve ser direcionado ao novo scaffold. O antigo deve ser preservado ate que a migracao esteja completa e validada.

---

## 2. Stack Tecnologica

| Camada | Tecnologia | Versao minima |
|---|---|---|
| Linguagem | Python | 3.12 |
| Interface | Streamlit | 1.40.0 |
| Validacao | Pydantic v2 | 2.9.0 |
| Configuracao | pydantic-settings | 2.6.0 |
| ORM | SQLAlchemy | 2.0 (declarative moderna) |
| Visualizacao | Plotly | 5.24.0 |
| Manipulacao de dados | Pandas | 2.2.0 |
| Banco (dev) | SQLite | built-in |
| Banco (producao alvo) | PostgreSQL | - |
| Testes | pytest | nao fixado em deps |

Nenhum framework HTTP esta em uso. O sistema nao expoe API REST, GraphQL ou gRPC.

---

## 3. Principios de Engenharia

**Arquitetura em camadas com influencia DDD**

```
Apresentacao    ->  app/pages/, pages/
Servico         ->  src/services/
Repositorio     ->  src/repositories/
Dominio         ->  src/domain/ (entidades puras, enums, regras de negocio)
Infraestrutura  ->  src/config/ (database, settings)
Ingestao        ->  src/ingestion/ (pipeline, readers, normalizer, parser)
Validacao       ->  src/validation/
Analitica       ->  src/analytics/
```

Cada camada tem responsabilidade unica e definida. Dependencias fluem de cima para baixo: apresentacao depende de servicos; servicos dependem de repositorios; repositorios dependem de modelos ORM; dominio nao depende de nenhuma camada de infraestrutura.

**Principios ativos:**

- Entidades de dominio sao dataclasses imutaveis (`frozen=True`).
- Regras de negocio vivem exclusivamente em `src/domain/rules.py`.
- Acesso a dados e mediado pelo padrao Repository — nenhuma camada acima de `repositories/` deve escrever queries diretamente.
- O pipeline de ingestao e stateless e retorna um resultado estruturado; efeitos colaterais (escrita no banco) devem ser responsabilidade da camada de servico.
- Configuracao sensivel ao ambiente e gerenciada via `pydantic-settings` com `.env`; nunca via constantes hard-coded no codigo-fonte.

---

## 4. Padroes de Seguranca

**Validacao de entrada**

Toda importacao de dado externo passa por validacao Pydantic antes de qualquer processamento:

- `TransactionImportSchema` em `src/validation/schemas.py` enforces tipos, ranges e tamanhos de campo.
- `validate_dataframe()` em `src/validation/validators.py` verifica presenca de colunas obrigatorias antes da validacao linha a linha.
- Formato de arquivo e validado por lista branca de extensoes (`SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".json"}`).

**Prevencao de injecao SQL**

- Toda interacao com banco de dados deve usar SQLAlchemy ORM ou `select()` parametrizado.
- `text()` com SQL literal e permitido apenas para queries completamente estaticas, sem concatenacao de input do usuario.
- Nunca formatar strings de usuario diretamente em queries.

**Gestao de segredos**

- `DATABASE_URL` e qualquer credencial devem estar em `.env` (nao versionado).
- Um arquivo `.env.example` documentando as variaveis esperadas deve existir no repositorio.
- Nenhum segredo deve ser hard-coded ou logado.

**Controle de acesso**

O sistema e projetado para uso local single-user. Nao ha camada de autenticacao. Se o projeto evoluir para multi-usuario, autenticacao e autorizacao devem ser adicionadas antes de qualquer exposicao de endpoint.

**Dependencias**

- Manter dependencias atualizadas regularmente.
- Nao adicionar bibliotecas desnecessarias — cada dependencia aumenta superficie de ataque e custo de manutencao.

---

## 5. Padroes de Manutenabilidade

- **Modularidade:** cada modulo tem responsabilidade unica. Nao misturar logica de apresentacao, negocio e persistencia no mesmo arquivo.
- **Baixo acoplamento:** servicos recebem repositorios por injecao de dependencia. Nunca instanciar repositorios dentro de funcoes de negocio.
- **Funcoes focadas:** funcoes devem fazer uma coisa. Funcoes de analytics em `src/analytics/` recebem DataFrames e retornam DataFrames ou valores — sem efeitos colaterais de I/O.
- **Sem estado global mutavel:** configuracao e provida via `Settings` singleton; sessoes de banco sao criadas por request/operacao, nunca mantidas globalmente.
- **Tratamento de erros estruturado:** o pipeline de ingestao retorna um `ErrorReport` tipado — nunca levante excecoes silenciosas ou retorne strings de erro nao tipadas.
- **Logging:** toda operacao de ingestao, erro de validacao e falha de persistencia deve ser registrada via modulo `logging` padrao do Python. Logs nao foram implementados ainda — esta e uma lacuna critica a se preencher.

---

## 6. Convencoes de Codigo

| Elemento | Convencao | Exemplo |
|---|---|---|
| Arquivos | snake_case | `ingestion_service.py` |
| Classes | PascalCase | `TransactionModel`, `IngestionPipeline` |
| Funcoes e metodos | snake_case | `validate_dataframe()`, `monthly_net_result()` |
| Constantes | UPPER_CASE | `REQUIRED_COLUMNS`, `SUPPORTED_EXTENSIONS` |
| Membros de Enum | UPPER_CASE | `INCOME`, `PRO_LABORE` |
| Paginas Streamlit | prefixo numerico + snake_case | `01_dashboard_geral.py` |
| Idioma do codigo | Ingles | nomes de variaveis, classes, funcoes |
| Idioma da interface | Portugues brasileiro | labels, mensagens de erro ao usuario |
| Idioma da documentacao | Portugues brasileiro | docstrings, comentarios |

**Annotations de tipo sao obrigatorias** em todas as assinaturas de funcao e metodo no novo scaffold. O uso de `Any` deve ser evitado.

**Imports** devem seguir a ordem: stdlib -> third-party -> projeto interno. Sem imports circular.

---

## 7. Boas Praticas Especificas da Stack

**Python / Pydantic v2**

- Use `model_validator` e `field_validator` para regras de validacao complexas; nao implemente logica de validacao fora do schema.
- `Field(gt=0)`, `Field(min_length=...)` para constraints simples — evita codigo de validacao manual redundante.
- Prefira `model_config = ConfigDict(...)` em vez do inner class `Config` legado.

**SQLAlchemy 2.0**

- Use `Mapped[T]` e `mapped_column()` em todos os modelos ORM novos.
- Gerencie sessoes com context manager (`with session_factory() as session:`).
- Nunca exponha o objeto `Session` fora da camada de repositorio.
- Para migracao de schema em producao, use Alembic — `create_all()` e aceitavel apenas em desenvolvimento.

**Pandas**

- Declare dtype explicitamente ao ler arquivos (`dtype={"amount": "float64"}`).
- Evite iteracao linha a linha (`iterrows`, `apply` com lambda complexo); prefira operacoes vetorizadas.
- Nao modifique DataFrames recebidos como parametro — retorne copias transformadas.

**Streamlit**

- Estado de aplicacao deve usar `st.session_state` com chaves tipadas.
- Operacoes pesadas (leitura de banco, calculos de analytics) devem ser decoradas com `@st.cache_data`.
- Paginas nao devem conter logica de negocio — apenas orquestracao de UI e chamadas a servicos.

---

## 8. Diretrizes para Evolucao do Projeto

**Prioridade imediata (pre-requisito para substituir o scaffold antigo):**

1. Implementar os metodos de `TransactionService` em `src/services/transaction_service.py`.
2. Conectar `IngestionPipeline` a um repositorio para persistencia de registros validados.
3. Implementar as paginas de `app/pages/` consumindo os servicos do novo scaffold.
4. Substituir o entry point raiz `streamlit_app.py` pelo `app/streamlit_app.py` quando as paginas estiverem funcionais.
5. Remover `src/fin_dashboard/` e `pages/` apos validacao completa da migracao.

**Migracao de banco:**

- Adicionar Alembic ao projeto antes de qualquer alteracao de schema em ambiente com dados reais.
- O conflito entre os dois ORM models mapeando para `"transactions"` deve ser resolvido antes do uso conjunto.

**Testes:**

- Adicionar `pytest` e `pytest-cov` como dev dependencies no `Pipfile`.
- Criar `pytest.ini` ou secao `[tool.pytest.ini_options]` em `pyproject.toml`.
- Cobrir pelo menos: happy path do pipeline de ingestao, validadores de schema, regras de dominio, e funcoes de analytics criticas.

**Infraestrutura:**

- Adicionar `.env.example` ao repositorio.
- Adicionar CI basico com GitHub Actions: lint (ruff ou flake8), type check (mypy), testes.
- Adicionar `Makefile` ou `justfile` com targets: `run`, `test`, `lint`, `migrate`.

---

## 9. Melhorias Sugeridas com Justificativa Tecnica

| Melhoria | Justificativa |
|---|---|
| Adicionar `logging` estruturado | Operacoes de ingestao sem logging tornam diagnostico de falhas em producao impossivel. |
| Adicionar Alembic para migracoes | `create_all()` e destrutivo em producao; sem migracao, evolucao de schema exige recriacao do banco. |
| Fixar versoes de dependencias (pin) | `>= 2.9.0` permite updates com breaking changes silenciosos; use versoes fixas em `requirements.txt` para reproducibilidade. |
| Adicionar `.env.example` | Engenheiros novos nao sabem quais variaveis de ambiente configurar sem um template documentado. |
| Adicionar `pyproject.toml` | Centraliza configuracao de pytest, mypy, ruff; elimina arquivos de configuracao dispersos. |
| Implementar logging no pipeline | `IngestionPipeline.run()` nao registra nenhum evento — falhas silenciosas sao impraticaveis. |
| Adicionar type checking com mypy | O projeto usa annotations de tipo mas sem verificacao estatica; mypy previne regressoes de tipos em refatoracoes. |
| Criar `IngestionPipeline.persist()` | O pipeline valida mas nao persiste — a ausencia deste metodo e a maior lacuna funcional do novo scaffold. |
| Adicionar `conftest.py` com fixtures de DB | Testes de integracao precisam de um banco SQLite em memoria compartilhado; sem fixtures centralizadas, cada teste gerencia seu proprio estado. |
| Remover `src/fin_dashboard/` apos migracao | Manter dois scaffolds paralelos aumenta custo cognitivo e risco de inconsistencia entre implementacoes. |
