# Dashboard

## Estrutura do Painel

O Ponte Nexus é um dashboard multipage do Streamlit. A navegação é feita pelo menu lateral. Todas as páginas carregam dados diretamente do banco via `src/analytics/loader.py` com cache de 30 segundos (`@st.cache_data(ttl=30)`).

---

## Páginas

### Página Inicial

**Arquivo:** `app/streamlit_app.py`

Ponto de entrada da aplicação. Exibe uma visão descritiva das seções disponíveis e orienta o usuário a importar dados antes de explorar os indicadores.

---

### 1. Dashboard Geral

**Arquivo:** `app/pages/01_dashboard_geral.py`

Visão consolidada do período completo com dados de todas as entidades.

**Indicadores (KPIs):**

| Métricas | Fonte |
|---|---|
| Total recebido pela PJ | Soma das transações do tipo `receita` |
| Total recebido pela PF | Soma de `pro_labore` + `dividendos` |
| Total de despesas | Soma das transações do tipo `despesa` |
| Saldo do período | Receitas PJ − Despesas |

**Gráficos:**

| Gráfico | Tipo | Descrição |
|---|---|---|
| Participação das Empresas (PJ) | Donut (pizza) | Distribuição percentual das receitas por entidade PJ |
| Resultado Mensal | Barras | Receitas − Despesas por mês |
| Despesas por Categoria | Pizza | Proporção de despesas agrupadas por categoria |
| Receitas vs Despesas | Barras agrupadas | Evolução mensal comparando receitas e despesas |

**Exportação:** botão para download do dashboard em PDF.

---

### 2. Fluxo PF ↔ PJ

**Arquivo:** `app/pages/02_fluxo_pf_pj.py`

Analisa transferências, aportes e retiradas entre Pessoa Física e Jurídica.

**Indicadores:**

| Métrica | Descrição |
|---|---|
| PF → PJ (aportes / empréstimos) | Total que a PF enviou para a PJ |
| PJ → PF (retiradas / dividendos) | Total que retornou para a PF |
| Saldo retornado à PF | PJ→PF − PF→PJ |

**Gráficos:**

| Gráfico | Tipo | Descrição |
|---|---|---|
| Volume por Tipo de Fluxo | Barras | Total por tipo de transação de fluxo cruzado |
| Evolução Mensal por Tipo | Barras empilhadas | Volume mensal por tipo de fluxo |

**Tipos de fluxo analisados:** `transferencia_pf_pj`, `transferencia_pj_pf`, `aporte_pf_pj`, `emprestimo_pf_pj`, `dividendos`, `pro_labore`.

---

### 3. Distribuição de Renda

**Arquivo:** `app/pages/03_distribuicao_renda.py`

Foco em pró-labore e dividendos — as modalidades de remuneração da PF via PJ.

**Indicadores:**

| Métrica | Transação |
|---|---|
| Pró-Labore | `pro_labore` |
| Dividendos | `dividendos` |
| Total Distribuído | soma dos dois |

**Gráficos:**

| Gráfico | Tipo | Descrição |
|---|---|---|
| Proporção Pró-Labore vs Dividendos | Donut | Participação percentual de cada modalidade |
| Evolução Mensal | Barras agrupadas | Valores mensais por modalidade |

---

### 4. Investimentos PF na PJ

**Arquivo:** `app/pages/04_investimentos_pf_pj.py`

Acompanha aportes de capital e empréstimos que a Pessoa Física realizou para a Pessoa Jurídica.

**Indicadores:**

| Métrica | Transação |
|---|---|
| Aportes | `aporte_pf_pj` |
| Empréstimos | `emprestimo_pf_pj` |
| Total Investido | soma dos dois |

**Gráficos:**

| Gráfico | Tipo | Descrição |
|---|---|---|
| Evolução Temporal | Barras agrupadas | Volume mensal por tipo de investimento |

**Tabela:** lista de transações individuais com data, tipo, entidades, valor e descrição.

---

### 5. Lançamentos

**Arquivo:** `app/pages/06_lancamentos.py`

Lista completa de todos os lançamentos com filtros interativos.

**Filtros disponíveis:**

| Filtro | Controle |
|---|---|
| Período | Seletor de intervalo de datas |
| Categoria | Multiselect |
| Origem (PF / PJ) | Multiselect |

**Colunas exibidas:** Data · Tipo · Descrição · Categoria · Entidade · Origem · Valor · Moeda.

**Exportação:** botão para download da tabela filtrada em XLSX.

---

### 6. Importação de Dados

**Arquivo:** `app/pages/05_importacao_dados.py`

Interface para upload de arquivos de lançamentos.

**Fluxo:**

1. Usuário seleciona arquivo (CSV, XLSX ou JSON).
2. O sistema exibe pré-visualização das primeiras 10 linhas.
3. Ao clicar em **Importar**, o pipeline valida e persiste os dados.
4. O resultado exibe quantidade de registros inseridos, ignorados e erros com número de linha.

---

## Cache e Atualização de Dados

Todas as páginas usam `@st.cache_data(ttl=30)` — os dados são recarregados do banco a cada 30 segundos. Após uma importação bem-sucedida, o cache é limpo imediatamente via `st.cache_data.clear()`.

---

## Comportamento com Banco Vazio

Todas as páginas verificam se o DataFrame está vazio e exibem uma mensagem orientando o usuário a importar dados antes de renderizar qualquer gráfico.
