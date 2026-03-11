# Dashboard Improvement Prompt

Purpose:
Refatorar e melhorar o dashboard financeiro da aplicação.

Use when:
- melhorar UX
- adicionar métricas
- melhorar visualização de dados

Você está atuando como um Engenheiro de Software Senior responsável por revisar e melhorar esta aplicação.

Seu objetivo é analisar o projeto atual e realizar melhorias estruturais na aplicação, mantendo a arquitetura existente sempre que possível.

As alterações devem priorizar:

- clareza
- manutenabilidade
- organização do código
- melhoria da experiência do usuário
- consistência de nomenclatura

Evite mudanças estruturais desnecessárias.

------------------------------------------------

FASE 1 — ANÁLISE DO PROJETO

Antes de realizar qualquer alteração:

1. Analise a arquitetura atual do projeto.
2. Identifique as camadas existentes (modelos, serviços, UI, etc).
3. Identifique pontos de melhoria no dashboard.
4. Avalie consistência das nomenclaturas utilizadas.

Somente após essa análise proponha as alterações.

------------------------------------------------

FASE 2 — PADRONIZAÇÃO DE NOMENCLATURA

A nomenclatura das tabelas e entidades deve seguir:

- idioma português
- padrão de nomenclatura das PEP do Python
- nomes claros e sem abreviações desnecessárias

Exemplos esperados:

lancamentos  
categorias  
empresas  
pessoa_fisica  

Evitar nomes genéricos ou inconsistentes.

------------------------------------------------

FASE 3 — MELHORIAS NO DASHBOARD

O dashboard principal precisa ser redesenhado para parecer um painel analítico profissional.

A página inicial deve conter:

1. Indicadores principais do período

- total recebido pela Pessoa Jurídica
- total recebido pela Pessoa Física
- total de despesas
- saldo do período

2. Gráfico de participação das empresas

Um gráfico de pizza mostrando a participação de cada PJ na geração de renda.

3. Últimos lançamentos

Uma tabela com os 10 lançamentos mais recentes contendo:

- data
- descrição
- categoria
- valor
- origem (PF ou PJ)

------------------------------------------------

FASE 4 — NOVA ABA DE LANÇAMENTOS

Criar uma aba dedicada para visualização de lançamentos.

Funcionalidades:

- lista completa de lançamentos
- filtro por período
- filtro por categoria
- filtro por entidade (PF ou PJ)

------------------------------------------------

FASE 5 — PERSONALIZAÇÃO DA INTERFACE

Na página inicial deve aparecer uma saudação personalizada:

Bom dia  
Boa tarde  
Boa noite  

A saudação deve considerar:

- horário atual
- nome da pessoa física
- sexo definido no cadastro

Exemplo:

"Bom dia, João."

Também deve aparecer uma pequena lista com as Pessoas Jurídicas vinculadas.

------------------------------------------------

FASE 6 — CONTROLE DE TEMA

Adicionar alternância de tema na interface:

- tema claro
- tema escuro

Implementar botão de alternância visível no dashboard.

------------------------------------------------

FASE 7 — EXPORTAÇÃO DE DADOS

Adicionar dois botões no dashboard.

Exportar Excel

Exportar os dados do painel em formato Excel.

Exportar PDF

Exportar o painel visual atual em formato PDF.

------------------------------------------------

FASE 8 — DEFINIÇÃO DE METAS

Permitir que o usuário defina metas financeiras.

Exemplos:

- meta de ganhos
- limite de despesas
- meta de rendimento

Essas metas devem ser utilizadas para comparação com os resultados do período.

------------------------------------------------

FASE 9 — RANKINGS FINANCEIROS

Adicionar rankings no painel.

Ranking de ganhos

Mostrar as categorias com maior geração de receita.

Ranking de despesas

Mostrar as categorias com maior gasto.

------------------------------------------------

FASE 10 — AGRUPAMENTO DO PERÍODO

Mostrar no painel um resumo consolidado do período selecionado:

Total ganho  
Total expendido  
Saldo do período  

Esses indicadores devem aparecer de forma destacada no dashboard.

------------------------------------------------

REGRAS IMPORTANTES

- manter código simples
- evitar complexidade desnecessária
- manter organização modular
- preservar arquitetura atual do projeto

------------------------------------------------

FORMATO DE SAÍDA

1. Descrição das melhorias propostas
2. Alterações necessárias na estrutura do código
3. Trechos de código modificados ou criados
4. Mudanças no dashboard
5. Melhorias adicionais recomendadas