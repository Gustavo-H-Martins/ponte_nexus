# UX Priorities — Ponte Nexus

> **Propósito:** Este documento é o insumo de trabalho para as correções de experiência do usuário. Cada prioridade contém diagnóstico, proposta e critério de aceitação mensurável.

**Data de elaboração:** 15/03/2026
**Baseado em:** Diagnóstico do Product Specialist + análise do scaffold `app/`

---

## Visão Geral

O produto funciona tecnicamente, mas apresenta vocabulário de engenheiro exposto ao usuário final, navegação que não comunica valor, e ausência de orientação para novos usuários. As correções abaixo são organizadas em três blocos: **Nomenclatura e Navegação**, **Comportamento da Interface** e **Jornada Guiada**.

---

## BLOCO 1 — Nomenclatura e Navegação

### UX-01 · Renomear páginas do menu lateral

**Prioridade:** CRÍTICA — afeta a primeira impressão de qualquer usuário novo.

**Diagnóstico:**
Os nomes atuais das páginas usam siglas técnicas (PF, PJ) e termos contábeis sem contexto para quem não conhece o sistema. Um usuário leigo que acessa pela primeira vez não entende o que encontrará em cada tela.

**Mapeamento atual → proposto:**

| Arquivo | Nome atual no menu | Nome proposto | Razão |
|---------|--------------------|---------------|-------|
| `01_dashboard_geral.py` | `Dashboard Geral` | `Início` ou `Visão Geral` | "Dashboard" é jargão técnico; "Início" é universal |
| `02_fluxo_pf_pj.py` | `Fluxo PF ↔ PJ` | `Transferências Pessoais e Empresa` | Elimina siglas; explica o que é |
| `03_distribuicao_renda.py` | `Distribuição de Renda` | `Minha Remuneração` | Fala diretamente com o usuário PF |
| `04_investimentos_pf_pj.py` | `Investimentos PF na PJ` | `Aportes na Empresa` | Mais direto e sem siglas |
| `05_importacao_dados.py` | `Importação de Dados` | `Importar Extrato` | Linguagem de usuário bancário |
| `06_lancamentos.py` | `Lançamentos` | `Histórico` ou `Extrato` | Familiar para usuário de app bancário |
| `07_novo_lancamento.py` | `Novo Lançamento` | `Registrar Transação` | Mais claro sobre a ação realizada |
| `08_painel_pessoal.py` | `Painel Pessoal` | `Meu Bolso` ou `Finanças Pessoais` | Tom pessoal, diferencia do contexto empresa |

**Como funciona no Streamlit:**
O nome exibido no menu lateral é derivado do nome do arquivo Python (removendo o prefixo numérico e substituindo `_` por espaço). Para alterar o nome exibido sem renomear o arquivo, é necessário definir `st.set_page_config(page_title=...)` **e** usar a configuração de páginas via `st.navigation()` no Streamlit ≥ 1.36, que permite `title` por página — ou renomear os arquivos mantendo o prefixo numérico de ordenação.

**Implementação recomendada:**
Migrar de páginas por convenção de arquivo para `st.navigation()` com objetos `st.Page(...)` no `streamlit_app.py`. Isso desacopla o nome exibido do nome do arquivo e permite agrupar páginas em seções.

**Exemplo de estrutura proposta:**

```python
# app/streamlit_app.py
pages = st.navigation({
    "Pessoal": [
        st.Page("pages/08_painel_pessoal.py",   title="Meu Bolso",          icon="👤"),
        st.Page("pages/03_distribuicao_renda.py", title="Minha Remuneração", icon="💰"),
    ],
    "Empresa": [
        st.Page("pages/01_dashboard_geral.py",    title="Visão Geral",       icon="📊"),
        st.Page("pages/02_fluxo_pf_pj.py",        title="Transferências",    icon="🔄"),
        st.Page("pages/04_investimentos_pf_pj.py", title="Aportes",          icon="📈"),
    ],
    "Operações": [
        st.Page("pages/06_lancamentos.py",         title="Extrato",          icon="📋"),
        st.Page("pages/07_novo_lancamento.py",     title="Registrar",        icon="✏️"),
        st.Page("pages/05_importacao_dados.py",    title="Importar Extrato", icon="📂"),
    ],
})
pages.run()
```

**Critério de aceitação:**

- [ ] Usuário vê grupos "Pessoal", "Empresa" e "Operações" no menu lateral.
- [ ] Nenhum nome de menu contém siglas PF ou PJ sem explicação contextual.
- [ ] Nenhum nome de menu contém o termo "Lançamento" ou "Dashboard" sem substituição.

---

### UX-02 · Subtítulos e descrições das páginas

**Prioridade:** ALTA

**Diagnóstico:**
Os subtítulos atuais usados em `page_header()` descrevem o mecanismo, não o benefício. Exemplo: `"Transferências, aportes e retiradas entre Pessoa Física e Jurídica"` — o usuário sabe o que o sistema faz, não o que ele ganha.

**Mapeamento atual → proposto:**

| Página | Subtítulo atual | Subtítulo proposto |
|---|---|---|
| Dashboard Geral | `Visão consolidada do período` | `Como estão suas finanças este mês` |
| Fluxo PF ↔ PJ | `Transferências, aportes e retiradas entre PF e PJ` | `Dinheiro que circulou entre você e sua empresa` |
| Distribuição de Renda | `Pró-labore e dividendos distribuídos no período` | `Quanto você retirou da empresa este mês` |
| Investimentos PF na PJ | `Aportes e empréstimos da PF para a PJ` | `Capital que você investiu na empresa` |
| Importação de Dados | `Envie um arquivo CSV, XLSX ou JSON com seus lançamentos` | `Importe o extrato do seu banco ou planilha` |
| Lançamentos | `Lista completa com filtros por período, categoria e entidade` | `Tudo que entrou e saiu nas datas selecionadas` |
| Novo Lançamento | *(verificar)* | `Registre uma receita, despesa ou transferência` |
| Painel Pessoal | *(verificar)* | `Sua vida financeira pessoal em um lugar só` |

**Critério de aceitação:**

- [ ] Nenhum subtítulo contém termos contábeis sem tradução para linguagem cotidiana.
- [ ] Todos os subtítulos respondem "o que eu vejo aqui?" do ponto de vista do usuário.

---

## BLOCO 2 — Comportamento da Interface

### UX-03 · Ocultar barra lateral em páginas de ação

**Prioridade:** ALTA — melhora foco nas páginas de formulário e importação.

**Diagnóstico:**
Em páginas de ação como "Registrar Transação" (`07_novo_lancamento.py`) e "Importar Extrato" (`05_importacao_dados.py`), a barra lateral está sempre visível e compete com o conteúdo principal. Em telas menores, isso reduz significativamente a área útil do formulário.

**Páginas candidatas a sidebar oculta:**

| Página | Justificativa |
|---|---|
| `07_novo_lancamento.py` | Formulário focado; usuário não precisa navegar durante o preenchimento |
| `05_importacao_dados.py` | Upload de arquivo é ação única; sidebar distrai |
| Onboarding (wizard) | Fluxo guiado não deve ter distrações de navegação |

**Implementação:**
Streamlit permite controle via `st.set_page_config(initial_sidebar_state="collapsed")` por página. Para ocultar completamente (não apenas recolher), é necessário injetar CSS:

```python
# Ocultar botão de expandir sidebar (sidebar invisível)
st.markdown(
    """
    <style>
    [data-testid="collapsedControl"] { display: none; }
    [data-testid="stSidebar"] { display: none; }
    </style>
    """,
    unsafe_allow_html=True,
)
```

**Variante recomendada — sidebar recolhida, não oculta:**
Usar `initial_sidebar_state="collapsed"` é mais seguro pois mantém a navegação acessível ao usuário que quiser. Ocultar completamente pode causar confusão (usuário não sabe como voltar ao menu).

**Proposta de implementação segura:**
Criar uma variável de controle no `ui.py`:

```python
def hide_sidebar_on_focus_pages() -> None:
    """Recolhe sidebar em páginas de ação para maximizar área do formulário."""
    st.set_page_config(initial_sidebar_state="collapsed")
    # Mantém o botão visível para o usuário poder abrir se quiser
```

**Critério de aceitação:**

- [ ] Ao abrir "Registrar Transação", sidebar aparece recolhida por padrão.
- [ ] Ao abrir "Importar Extrato", sidebar aparece recolhida por padrão.
- [ ] O botão de expansão da sidebar permanece visível (navegação não bloqueada).
- [ ] Páginas analíticas (Dashboard, Fluxo, etc.) continuam com sidebar expandida por padrão.

---

### UX-04 · Estado vazio informativo (empty states)

**Prioridade:** ALTA — afeta diretamente a primeira experiência.

**Diagnóstico:**
Quando não há dados (banco vazio ou filtro sem resultados), algumas páginas exibem apenas uma tabela vazia ou nenhuma mensagem. O usuário não sabe se é um erro, se precisa importar dados ou se o filtro está errado.

**Páginas afetadas:**

| Página | Comportamento atual | Comportamento esperado |
|---|---|---|
| `06_lancamentos.py` | Tabela vazia | Mensagem "Nenhum lançamento encontrado. [Registrar] ou [Importar]" com botões de ação |
| `02_fluxo_pf_pj.py` | Gráfico vazio | "Não há transferências no período. Ajuste o filtro ou [Registre uma transferência]." |
| `03_distribuicao_renda.py` | Gráfico vazio/erro | "Nenhuma distribuição de renda no período selecionado." |
| `04_investimentos_pf_pj.py` | Gráfico vazio/erro | "Nenhum aporte ou empréstimo registrado no período." |
| `08_painel_pessoal.py` | *(verificar)* | "Configure seu perfil primeiro. [Ir para configuração]" |

**Padrão de implementação sugerido:**

```python
def render_empty_state(
    message: str,
    action_label: str | None = None,
    action_page: str | None = None,
) -> None:
    st.info(f"📭 {message}")
    if action_label and action_page:
        if st.button(action_label, type="primary"):
            st.switch_page(action_page)
```

**Critério de aceitação:**

- [ ] Toda página analítica exibe mensagem contextual quando não há dados.
- [ ] Mensagens de estado vazio incluem, quando aplicável, botão de ação (ex: "Registrar", "Importar").
- [ ] Nenhuma página exibe erro Python não tratado para estado de banco vazio.

---

### UX-05 · Feedback de ações do usuário

**Prioridade:** MÉDIA

**Diagnóstico:**
Algumas ações (salvar lançamento, importar arquivo) exibem `st.success()` mas o contexto some ao recarregar. Não há confirmação visual clara do que foi salvo, nem histórico de ações recentes.

**Melhorias propostas:**

- Após salvar um lançamento manual, exibir um resumo compacto: `"✅ Despesa de R$ 350,00 em Alimentação registrada."` com opção `[Registrar outro]` e `[Ver no extrato]`.
- Após importação bem-sucedida, exibir contador de registros importados e link direto para o extrato.
- Usar `st.toast()` (disponível no Streamlit ≥ 1.29) para notificações não-bloqueantes.

**Critério de aceitação:**

- [ ] Salvar lançamento → exibe toast com resumo da transação.
- [ ] Importar arquivo → exibe contagem de registros importados e link para extrato.
- [ ] Erros de validação são exibidos no campo correspondente, não apenas no topo da página.

---

## BLOCO 3 — Jornada Guiada (Onboarding)

### UX-06 · Aprimorar onboarding — fluxo completo de 4 passos

**Prioridade:** CRÍTICA — é o principal ponto de abandono de novos usuários.

**Diagnóstico:**
O onboarding atual (`01_dashboard_geral.py`) exibe 3 cards de status (Perfil PF, Empresa, Importar) mas não guia o usuário passo a passo de forma narrativa. A sequência necessária para o sistema funcionar não está clara:

1. Criar entidade PF (quem sou eu)
2. Criar entidade PJ — opcional (tenho empresa?)
3. Criar fontes de renda (de onde vem meu dinheiro?)
4. Importar dados ou registrar primeiro lançamento

**Estado atual:**

- Passo 1 (entidade PF) tem formulário embutido. ✅
- Passo 2 (entidade PJ) tem formulário embutido. ✅
- Passo 3 (fontes de renda) não existe na UI ainda. ❌
- Passo 4 (importar/registrar) tem link, mas não é narrativo. ⚠️

**Proposta de melhoria:**

```
Wizard de 4 etapas visível no topo da página:

[1. Seu perfil] → [2. Sua empresa] → [3. Fontes de renda] → [4. Primeiro dado]
    ✅ Concluído      ⏳ Em andamento    ○ Pendente             ○ Pendente
```

Usar `st.progress()` ou cards com checkmarks para indicar progresso.

**Conteúdo narrativo para cada passo:**

| Passo | Título | Mensagem de contexto |
|---|---|---|
| 1 | Olá! Vamos começar? | "Primeiro, precisamos saber quem você é. Informe seu nome para criar seu perfil pessoal." |
| 2 | Você tem empresa? | "Se você é sócio, MEI ou tem CNPJ, adicione sua empresa. Isso nos permite separar seus gastos pessoais dos empresariais. (Pode pular)" |
| 3 | De onde vem seu dinheiro? | "Adicione suas fontes de renda: salário, freelance, dividendos. Isso torna suas análises muito mais precisas." |
| 4 | Ótimo! Agora só falta um dado. | "Você pode importar um extrato bancário em CSV/XLSX ou registrar sua primeira transação manualmente." |

**Onde fica o wizard:**

- A lógica já está no `01_dashboard_geral.py`. Deve ser extraída para um componente `_render_onboarding()` em `app/ui.py` para reuso.
- O wizard aparece **somente** quando o banco está vazio (0 transações). Após o primeiro dado, some definitivamente.

**Critério de aceitação:**

- [ ] Novo usuário vê wizard ao abrir o sistema pela primeira vez.
- [ ] Progresso do wizard é visual (indicador de etapa atual).
- [ ] Cada etapa tem texto explicativo em linguagem cotidiana, sem jargões.
- [ ] Ao finalizar todos os passos, o wizard desaparece e o dashboard normal é exibido.
- [ ] O wizard não aparece quando já existem transações cadastradas.

---

### UX-07 · Tutorial inline — dicas contextuais por página

**Prioridade:** MÉDIA — reduz curva de aprendizado após o onboarding.

**Diagnóstico:**
Após o onboarding, o usuário está sozinho. Não há dicas sobre o que os gráficos mostram, como interpretar os KPIs, ou qual filtro usar para uma análise específica.

**Proposta:**
Implementar um sistema de dicas contextuais usando `st.expander()` com ícone `ℹ️`:

```python
# Padrão para dica contextual
with st.expander("ℹ️ Como interpretar este gráfico", expanded=False):
    st.markdown("""
    **O que você vê aqui:**
    Este gráfico mostra o saldo líquido mensal — a diferença entre tudo que entrou 
    e tudo que saiu no período. Valores positivos (verde) indicam meses superavitários.
    
    **Dica:** Use o filtro de período acima para comparar semestres diferentes.
    """)
```

**Dicas prioritárias a implementar:**

| Página | Dica |
|---|---|
| Dashboard Geral | Como interpretar receita PJ vs receita PF |
| Fluxo PF ↔ PJ | O que são aportes vs transferências vs pró-labore |
| Distribuição de Renda | Diferença entre pró-labore e dividendos |
| Importação | Formato esperado do CSV (com link para template) |
| Novo Lançamento | Quando usar "Transferência" vs "Receita" |

**Critério de aceitação:**

- [ ] Cada página analítica tem ao menos uma dica contextual implementada.
- [ ] Dicas são recolhidas por padrão (não ocupam espaço quando não solicitadas).
- [ ] Dicas usam exemplos reais do contexto PF/PJ brasileiro.

---

### UX-08 · Documentação de uso — guia rápido em Markdown

**Prioridade:** MÉDIA — serve como referência e reduz suporte.

**Diagnóstico:**
Não existe guia de uso do produto para o usuário final. O `README.md` é técnico (instalação, stack). O `docs/` contém documentação de arquitetura, não de uso.

**Proposta:**
Criar `docs/guia-de-uso.md` com as seguintes seções:

```markdown
1. Primeiros passos (onboarding em texto)
2. Como importar seu extrato bancário
3. Como registrar uma transação manualmente
4. Como interpretar o Dashboard Geral
5. Como analisar o fluxo entre você e sua empresa
6. Como acompanhar sua remuneração
7. FAQ — Perguntas frequentes
```

**Opção alternativa (mais viável):**
Criar uma página Streamlit `09_ajuda.py` que exibe este guia inline com `st.markdown()` e âncoras por seção. Vantagens: fica acessível no próprio produto, sem precisar sair do app.

**Critério de aceitação:**

- [ ] Existe ao menos um guia de uso navegável (arquivo `.md` ou página Streamlit).
- [ ] O guia cobre os 3 fluxos principais: onboarding, importação e lançamento manual.
- [ ] O guia é linkado ou acessível a partir da tela de onboarding.

---

## BLOCO 4 — Páginas Ausentes com Alta Prioridade de UX

### UX-09 · Página de Orçamento por Categoria (P4)

**Prioridade:** ALTA — serviço `BudgetService` já existe, falta apenas a UI.

**Diagnóstico:**
`src/services/budget_service.py` e `BudgetModel` já estão implementados. A tela de configuração de orçamento está ausente.

**Proposta de página `09_orcamento.py`:**

```
Título: "Meu Orçamento"
Subtítulo: "Defina limites de gastos por categoria e acompanhe seu progresso"

Seção 1 — Definir meta
  [Selecionar categoria] [Valor limite R$] [Mês referência] [Salvar meta]

Seção 2 — Acompanhamento do mês atual
  Para cada categoria com meta:
    [Nome categoria] [Barra de progresso] [R$ gasto / R$ meta] [% utilizado]
    Se > 80%: barra laranja + aviso "⚠️ Atenção: 85% do orçamento utilizado"
    Se > 100%: barra vermelha + alerta "🔴 Limite ultrapassado"
```

**Critério de aceitação:**

- [ ] Usuário consegue definir orçamento mensal por categoria.
- [ ] Barras de progresso mostram % utilizado em tempo real.
- [ ] Alerta visual quando orçamento > 80%.
- [ ] Alerta visual diferenciado quando orçamento > 100%.

---

### UX-10 · Página de Fontes de Renda (P2)

**Prioridade:** ALTA — resolve o problema "de onde vem meu dinheiro?" de forma nomeada.

**Diagnóstico:**
`IncomeSourceModel` e `IncomeSourceRepository` já existem. Não há página de gestão nem análise por fonte.

**Proposta:**

Duas sub-seções na página `10_fontes_renda.py` ou integrada ao Painel Pessoal:

1. **Gestão de Fontes:** cadastro de fontes (salário, freelance, dividendos, etc.) com vinculação a entidade.
2. **Análise por Fonte:** gráfico de receitas por fonte de renda com ranking e comparação de períodos.

**Critério de aceitação:**

- [ ] Usuário consegue cadastrar fontes de renda nomeadas.
- [ ] Receitas podem ser vinculadas a uma fonte específica.
- [ ] Existem gráficos mostrando ranking e evolução por fonte.

---

## Resumo Executivo de Prioridades

| Código | Título | Prioridade | Esforço Estimado | Impacto |
|---|---|---|---|---|
| UX-01 | Renomear páginas do menu | CRÍTICA | Baixo (1–2h) | Alto |
| UX-06 | Aprimorar onboarding | CRÍTICA | Médio (4–6h) | Alto |
| UX-02 | Subtítulos orientados ao usuário | ALTA | Baixo (1h) | Médio |
| UX-03 | Sidebar recolhida em formulários | ALTA | Baixo (1h) | Médio |
| UX-04 | Empty states informativos | ALTA | Médio (3–4h) | Alto |
| UX-09 | UI de Orçamento por Categoria | ALTA | Médio (4–6h) | Alto |
| UX-10 | UI de Fontes de Renda | ALTA | Médio (4–6h) | Alto |
| UX-05 | Feedback de ações (toast) | MÉDIA | Baixo (2h) | Médio |
| UX-07 | Dicas contextuais inline | MÉDIA | Médio (3–4h) | Médio |
| UX-08 | Guia de uso / Página de Ajuda | MÉDIA | Médio (2–4h) | Médio |

### Sprint sugerido — Correções rápidas (< 1 dia de trabalho)

1. **UX-01** — Renomear menus usando `st.navigation()` com grupos
2. **UX-02** — Atualizar subtítulos das 8 páginas
3. **UX-03** — Adicionar `initial_sidebar_state="collapsed"` nas páginas `07` e `05`
4. **UX-04** — Empty state em `06_lancamentos.py` (o mais visível)

### Sprint sugerido — Jornada completa (1–3 dias de trabalho)

1. **UX-06** — Wizard de onboarding aprimorado com passo 3 (fontes de renda)
2. **UX-09** — Tela de orçamento (infra já existe)
3. **UX-10** — Tela de gestão e análise de fontes de renda

---

## Referências Técnicas

- Streamlit `st.navigation()`: <https://docs.streamlit.io/develop/api-reference/navigation/st.navigation>
- Streamlit `st.Page()`: <https://docs.streamlit.io/develop/api-reference/navigation/st.page>
- Streamlit `st.toast()`: <https://docs.streamlit.io/develop/api-reference/status/st.toast>
- Streamlit `st.switch_page()`: <https://docs.streamlit.io/develop/api-reference/navigation/st.switch_page>
- Serviços já implementados: `src/services/budget_service.py`, `src/repositories/income_source_repository.py`
- Modelos já implementados: `src/models/db_models.py` → `BudgetModel`, `IncomeSourceModel`
