# Ponte Nexus — Análise e Plano de Melhorias do Sistema

> Documento gerado em: 2026-03-15  
> Revisado por: engenharia (GitHub Copilot)

---

## 1. Análise da Arquitetura Atual

### Estrutura de Diretórios

```
ponte_nexus/
├── app/                    # UI Streamlit (scaffold ativo)
│   ├── streamlit_app.py    # Entry point + navegação st.navigation
│   ├── ui.py               # Componentes e utilitários visuais
│   ├── export.py           # Geração de PDF (fpdf2)
│   ├── icons/feather/      # SVGs Feather Icon
│   └── pages/              # 12 páginas Streamlit (01–12)
│
├── src/                    # Backend — camadas DDD
│   ├── config/             # Settings (Pydantic), engine SQLAlchemy
│   ├── domain/             # Entidades imutáveis + enums + regras de negócio
│   ├── models/             # ORM SQLAlchemy 2.0
│   ├── repositories/       # Acesso a dados (um repositório por entidade)
│   ├── services/           # Lógica de negócio (orquestração)
│   ├── ingestion/          # Pipeline de importação CSV/XLSX/JSON
│   ├── validation/         # Schemas Pydantic de validação de entrada
│   ├── analytics/          # Funções Pandas/Plotly para indicadores
│   └── fin_dashboard/      # Scaffold legado (APENAS DIRETÓRIOS VAZIOS)
│
├── pages/                  # Scaffold legado (DIRETÓRIO VAZIO)
├── tests/                  # Testes unitários e de integração (29 testes)
└── docs/                   # Documentação técnica
```

### Tecnologias

| Camada        | Tecnologia                   | Versão mínima |
|---------------|------------------------------|---------------|
| Interface     | Streamlit                    | 1.40.0        |
| ORM           | SQLAlchemy                   | 2.0           |
| Validação     | Pydantic + pydantic-settings | 2.x           |
| Análise       | Pandas                       | 2.2.0         |
| Gráficos      | Plotly                       | 5.24.0        |
| Banco (dev)   | SQLite                       | —             |
| Exportação    | fpdf2                        | 2.7.0         |
| Runtime       | Python                       | 3.12          |

### Entidades financeiras existentes

| Modelo                    | Tabela                  | Descrição                                      |
|---------------------------|-------------------------|------------------------------------------------|
| `EntityModel`             | `entidades`             | Pessoa Física (PF) ou Jurídica (PJ)            |
| `AccountModel`            | `contas`                | Conta vinculada a uma entidade                 |
| `CategoryModel`           | `categorias`            | Categorias de lançamento                       |
| `TransactionModel`        | `lancamentos`           | Transação financeira entre contas/entidades    |
| `PfPjRelationshipModel`   | `relacionamentos_pf_pj` | Vínculo PF ↔ PJ                               |
| `CompanyModel`            | `empresas`              | Dados adicionais PJ (CNPJ, tipo societário)    |
| `IncomeSourceModel`       | `fontes_renda`          | Fonte de renda nomeada por entidade            |
| `BudgetModel`             | `orcamentos`            | Meta mensal de gasto por categoria             |

### Sistema de autenticação

**Não existe.** O sistema não possui autenticação, sessão de usuário ou controle de acesso.  
Todos os dados são globais — qualquer pessoa com acesso à URL vê e edita tudo.

### Bugs corrigidos durante esta análise

| Arquivo | Bug | Corrigido |
|---------|-----|-----------|
| `app/pages/01_dashboard_geral.py` | `st.set_page_config` duplicado | ✅ |
| `app/pages/01_dashboard_geral.py` | `feather_icon` usada antes do import local | ✅ |
| `app/pages/02_fluxo_pf_pj.py` | `page_icon=FAVICON_IMG or feather_icon(...)` — SVG inválido no Streamlit | ✅ |
| `app/pages/03_distribuicao_renda.py` | Idem | ✅ |
| `app/pages/04_investimentos_pf_pj.py` | Idem | ✅ |
| `app/pages/05_importacao_dados.py` | Idem | ✅ |
| `app/streamlit_app.py` | Import de `feather_icon` sem uso | ✅ |

---

## 2. Arquivos Não Utilizados / Obsoletos

| Arquivo / Diretório | Localização | Motivo da Remoção |
|---------------------|-------------|-------------------|
| `src/fin_dashboard/ingestion/` | `src/fin_dashboard/` | Diretório vazio — remanescente do scaffold legado |
| `src/fin_dashboard/models/` | `src/fin_dashboard/` | Diretório vazio — remanescente do scaffold legado |
| `src/fin_dashboard/schemas/` | `src/fin_dashboard/` | Diretório vazio — remanescente do scaffold legado |
| `src/fin_dashboard/services/` | `src/fin_dashboard/` | Diretório vazio — remanescente do scaffold legado |
| `pages/` (diretório raiz) | `/` | Diretório vazio — scaffold original abandonado |
| `data/samples/sample_valid.xlsx.note.txt` | `data/samples/` | Nota de texto sem utilidade no repositório |
| `app/pages/12_planos.py` | `app/pages/` | Stub sem implementação real — apenas placeholder |

---

## 3. Melhorias Visuais

### Status atual

- `feather_icon()` em `app/ui.py` renderiza SVG via `st.markdown(unsafe_allow_html=True)` ✅  
- O Streamlit **não aceita SVG** nos parâmetros nativos `page_icon` (set_page_config) nem `icon` (st.Page)  
- Emojis `💠` sem semântica ainda presentes em algumas páginas como `page_icon`

### Ações pendentes — visuais

| # | Ação | Arquivo(s) | Prioridade |
|---|------|------------|------------|
| V-01 | Substituir `💠` por emoji semântico | `06_lancamentos.py`, `09_ajuda.py`, `10_orcamento.py`, `11_fontes_renda.py` | Média |
| V-02 | Garantir que `page_header()` cobre todas as páginas | Todos `app/pages/*.py` | Baixa |
| V-03 | Adicionar dark/light mode toggle explícito | `app/ui.py` | Baixa |

---

## 4. Modelo de Contas Financeiras

### Status atual

`AccountModel` possui apenas `entity_id`, `account_name` e `currency`.  
**Falta**: tipo de conta, descrição, status ativo/inativo.

### Proposta de alteração no modelo

```python
# Adicionar em src/domain/enums.py
class AccountType(str, Enum):
    CONTA_BANCARIA = "conta_bancaria"
    CAIXA          = "caixa"
    COFRE          = "cofre"
    INVESTIMENTOS  = "investimentos"
    PROVISAO       = "provisao"
    OUTRA          = "outra"
```

```python
# Alteração em src/models/db_models.py — AccountModel
class AccountModel(Base):
    __tablename__ = "contas"

    id:           Mapped[int]      = mapped_column(primary_key=True)
    entity_id:    Mapped[int]      = mapped_column(ForeignKey(FK_ENTITIES_ID), nullable=False)
    account_name: Mapped[str]      = mapped_column(String(255), nullable=False)
    account_type: Mapped[str]      = mapped_column(String(32), nullable=False, default="conta_bancaria")
    currency:     Mapped[str]      = mapped_column(String(3), nullable=False)
    description:  Mapped[str|None] = mapped_column(Text, nullable=True)
    is_active:    Mapped[bool]     = mapped_column(default=True, nullable=False)
```

**Impacto:** requer migração Alembic.  
Dados existentes recebem `account_type = "conta_bancaria"` e `is_active = true` via `ALTER TABLE`.

### Funcionalidades habilitadas

- Filtrar posição financeira por tipo de conta
- Desativar contas sem perder histórico de movimentações
- Exibir cards visuais distintos por tipo no dashboard

---

## 5. Proposta de Autenticação e Permissões

### 5.1 Modelo de usuário

```python
# Novo: src/models/db_models.py
class UserModel(Base):
    __tablename__ = "usuarios"

    id:            Mapped[int]      = mapped_column(primary_key=True)
    email:         Mapped[str]      = mapped_column(String(255), nullable=False, unique=True)
    password_hash: Mapped[str]      = mapped_column(String(255), nullable=False)  # bcrypt
    display_name:  Mapped[str]      = mapped_column(String(255), nullable=False)
    role:          Mapped[str]      = mapped_column(String(16), nullable=False, default="user")
    plan:          Mapped[str]      = mapped_column(String(16), nullable=False, default="free")
    is_active:     Mapped[bool]     = mapped_column(default=True, nullable=False)
    created_at:    Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
```

### 5.2 Papéis

| Role     | Permissões |
|----------|-----------|
| `user`   | Ver e editar apenas seus próprios dados. Cadastrar lançamentos e relatórios básicos. |
| `reader` | Visualizar dados de usuários que concederam acesso. Sem permissão de escrita. |
| `admin`  | Gerenciar todos os usuários, acessar qualquer dado, configurações do sistema. |

### 5.3 Planos

| Plano  | Recursos incluídos |
|--------|-------------------|
| `free` | Lançamentos manuais, relatórios básicos, 1 entidade PJ |
| `pro`  | Importação de extratos, múltiplas PJs, relatórios completos, exportação PDF |

### 5.4 Isolamento de dados (multi-tenant)

Todas as tabelas de dados ganham `owner_id` referenciando `usuarios.id`.  
Repositórios filtram por `owner_id` automaticamente — a UI nunca conhece o filtro diretamente.

### 5.5 Acesso de leitura compartilhado

```python
class UserReaderAccessModel(Base):
    __tablename__ = "acessos_leitura"

    id:         Mapped[int]      = mapped_column(primary_key=True)
    owner_id:   Mapped[int]      = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    reader_id:  Mapped[int]      = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    granted_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
```

### 5.6 Fluxo de autenticação

```
1. Usuário acessa o sistema sem sessão ativa
2. Redirecionado para tela de login/cadastro
3. Cadastro → plano FREE criado automaticamente
4. Login com email + senha → session_state["user_id"] e session_state["role"]
5. Todas as queries passam o user_id como parâmetro ao repositório
6. Logout → st.session_state limpo + st.rerun()
```

> **Biblioteca recomendada**: `streamlit-authenticator` (sem dependência Nova) ou implementação própria  
> com `bcrypt` para hash. Não requer JWT — `st.session_state` é suficiente para sessão single-server.

---

## 6. TODO Estruturado

### Prioridade CRÍTICA — app em estado quebrado

| ID   | Descrição | Motivo | Impacto | Status |
|------|-----------|--------|---------|--------|
| C-01 | Corrigir `page_icon=FAVICON_IMG or feather_icon(...)` em todas as páginas | SVG inválido no Streamlit | App quebra ao navegar | ✅ Concluído |
| C-02 | Remover `set_page_config` duplicado em `01_dashboard_geral.py` | Streamlit permite apenas uma chamada | Erro de runtime | ✅ Concluído |
| C-03 | Corrigir import de `feather_icon` antes do uso em `01_dashboard_geral.py` | `NameError` ao carregar onboarding | App quebra | ✅ Concluído |
| C-04 | Configurar Alembic para migrações de schema | `create_all()` em produção pode destruir dados | Perda de dados em atualização | ⏳ Pendente |
| C-05 | Eliminar `sys.path.insert` das páginas via `pyproject.toml` | Frágil, depende de CWD de execução | Falha silenciosa ao mover arquivos | ⏳ Pendente |

### Prioridade ALTA — funcionalidades essenciais ausentes

| ID   | Descrição | Motivo | Impacto |
|------|-----------|--------|---------|
| A-01 | Adicionar `account_type` ao `AccountModel` + enum `AccountType` | Sem tipo não há distinção bancária/caixa/investimentos | Modelo financeiro incompleto |
| A-02 | Adicionar `is_active` ao `AccountModel` | Impossível desativar conta sem apagar histórico | Integridade referencial |
| A-03 | Criar página de gestão de contas financeiras | Usuário não consegue criar/editar contas pela UI | Fluxo de cadastro bloqueado |
| A-04 | Criar página de gestão de entidades (PF/PJ) | Só é possível criar entidades no onboarding | Entidades não editáveis pós-cadastro |
| A-05 | Adicionar saldo calculado por conta no dashboard | Sem saldo visível não há controle financeiro real | Dashboard incompleto |

### Prioridade MÉDIA — qualidade e manutenibilidade

| ID   | Descrição | Motivo | Impacto |
|------|-----------|--------|---------|
| M-01 | Remover diretórios vazios de `src/fin_dashboard/` | Confusão de scaffold | Limpeza de repositório |
| M-02 | Remover diretório vazio `pages/` raiz | Idem | Limpeza de repositório |
| M-03 | Padronizar `page_icon` com emojis semanticamente corretos | `💠` sem significado | Consistência visual |
| M-04 | Cobrir `BudgetService`, `ManualEntryService`, `CatalogService` com testes | Serviços centrais sem cobertura | Qualidade de código |
| M-05 | Criar `pyproject.toml` e instalar projeto como pacote editável | Elimina `sys.path.insert` em todas as páginas | Manutenibilidade |

### Prioridade BAIXA — novas funcionalidades

| ID   | Descrição | Motivo | Impacto |
|------|-----------|--------|---------|
| B-01 | Implementar autenticação (login/cadastro + bcrypt) | Requisito fundamental para multi-usuário | Habilitador para produção |
| B-02 | Implementar `UserModel` + `owner_id` em todas as tabelas | Dados compartilhados é risco de privacidade | Segurança e isolamento |
| B-03 | Implementar papéis `user` / `reader` / `admin` | Sem permissões não há controle de acesso | Multi-tenant |
| B-04 | Implementar planos `free` / `pro` | Base para monetização | Funcionalidade futura |
| B-05 | Histórico de saldo por conta (posição no tempo) | Dashboard financeiro exige visão temporal | Funcionalidade analítica |
| B-06 | Implementar `12_planos.py` com funcionalidade real | Atualmente stub sem conteúdo | UX |

---

## 7. Sequência de Implementação Recomendada

```
Sprint 1 — Fundação técnica
  ├── C-04: Alembic setup + primeira migration
  ├── C-05 + M-05: pyproject.toml → elimina sys.path.insert
  ├── M-01 + M-02: limpeza de diretórios obsoletos
  └── M-03: padronização de page_icon

Sprint 2 — Modelo financeiro completo
  ├── A-01: AccountType enum + campo account_type + migration
  ├── A-02: is_active em AccountModel + migration
  ├── A-03: página gestão de contas (list / create / deactivate)
  └── A-04: página gestão de entidades (list / create / edit)

Sprint 3 — Autenticação e multi-usuário
  ├── B-01: UserModel + bcrypt + tela login/cadastro
  ├── B-02: owner_id nas tabelas + migrations
  └── B-03: papéis user / reader / admin + middleware

Sprint 4 — Dashboard avançado e cobertura
  ├── A-05: saldo calculado por conta
  ├── B-05: histórico de saldo
  ├── M-04: cobertura de testes de serviços
  └── B-06: página de planos funcional
```

---

## Convenções para Implementação

- Toda alteração de schema → migração Alembic correspondente obrigatória
- Novos modelos ORM → `Mapped[T]` + `mapped_column()` (SQLAlchemy 2.0)
- Senhas → `bcrypt` com salt (nunca MD5/SHA1/SHA256 puro)
- Segredos → `.env` (nunca no código-fonte nem no versionamento)
- Multi-tenant → filtro por `owner_id` no repositório, nunca na UI nem no serviço
- Testes → SQLite em memória via fixture em `tests/conftest.py`

