# ADR-001 — Escolha do Streamlit como camada de visualização

**Status:** Aceito  
**Data:** 2024  
**Autores:** Equipe Ponte Nexus

---

## Contexto

O Ponte Nexus é um dashboard financeiro para análise de fluxos entre PF e PJ, voltado inicialmente para uso interno por um número reduzido de usuários técnicos (sócios, contadores, gestores). A aplicação precisa:

- Exibir indicadores financeiros calculados a partir de dados importados.
- Permitir upload e validação de arquivos CSV, XLSX e JSON.
- Ser construída com Python puro, sem a necessidade de uma equipe frontend dedicada.
- Ter ciclos de iteração rápidos — novas páginas e indicadores adicionados com custo baixo.
- Ser implantável de forma simples, preferencialmente com um único processo.

---

## Decisão

Usar **Streamlit** como a camada de interface do usuário.

---

## Motivação

O sistema já usa Python 3.12, pandas e Plotly para toda a lógica analítica. O Streamlit permite construir interfaces web interativas diretamente em Python, reutilizando os mesmos objetos (DataFrames, figuras Plotly) sem conversão de formato ou camada de serialização adicional.

A alternativa de construir uma API REST + frontend JavaScript separaria o stack em duas bases de código com linguagens diferentes, aumentando o custo de manutenção sem benefício imediato dado o perfil de usuários inicialmente previsto.

---

## Alternativas Consideradas

### Dash (Plotly)

**Prós:**
- Integração nativa com Plotly.
- Maior controle sobre o layout (callbacks, componentes personalizados).
- Melhor suporte a interatividade complexa entre gráficos.

**Contras:**
- Curva de aprendizado maior (conceito de callbacks).
- Mais verboso para páginas simples.
- Requer mais código boilerplate para o mesmo resultado.

**Por que não foi escolhido:** para o caso de uso do Ponte Nexus — dashboards analíticos com filtros simples — o Streamlit entrega o mesmo resultado com metade do código.

### Apache Superset

**Prós:**
- Ferramenta madura de BI com interface visual para criação de dashboards.
- Suporte nativo a múltiplos bancos de dados.
- Não requer programação para criar visualizações básicas.

**Contras:**
- Requer implantação de um serviço separado (Docker, banco de metadados próprio).
- Customização avançada exige conhecimento de plugins React.
- Acoplamento ao modelo de dados via SQL direto — dificulta lógica de negócio em Python.
- Overhead operacional desproporcional ao tamanho do projeto.

**Por que não foi escolhido:** o overhead de operação e a separação entre a lógica Python e a interface gráfica criariam duas superfícies de manutenção sem ganho real para o estágio atual do produto.

### Metabase

**Prós:**
- Interface de usuário amigável para usuários não técnicos.
- Configuração rápida via Docker.

**Contras:**
- Sem suporte a lógica de negócio em Python.
- Customização muito limitada.
- Licença open source com restrições para uso comercial (BSL).

**Por que não foi escolhido:** o Ponte Nexus precisa de lógica de domínio Python (validação PF↔PJ, deduplicação, normalização) que não pode ser expressa como queries SQL simples.

### React + FastAPI

**Prós:**
- Máxima flexibilidade de UI/UX.
- Separação limpa entre frontend e backend.
- Escalável para times maiores.

**Contras:**
- Requer equipe com expertise em dois stacks diferentes.
- Custo de desenvolvimento muito mais alto.
- Sem benefício para o perfil de usuário atual.

**Por que não foi escolhido:** prematura para o estágio atual do produto. A arquitetura foi desenhada para facilitar essa transição futura caso necessário — a camada de serviços em `src/services/` é independente da UI e pode ser exposta via REST sem refatoração da lógica de negócio.

---

## Vantagens do Streamlit para Este Projeto

- **Produtividade:** nova página analítica em dezenas de linhas de Python puro.
- **Zero frontend:** sem HTML, CSS ou JavaScript obrigatório.
- **Integração nativa:** DataFrames e figuras Plotly são renderizados diretamente.
- **Upload de arquivos:** `st.file_uploader` integra-se diretamente com o pipeline de ingestão.
- **Cache declarativo:** `@st.cache_data` reduz consultas ao banco em páginas de múltiplos gráficos.
- **Estado simples:** `st.session_state` para filtros e estado entre reruns.
- **Deploy simples:** um único processo Python, sem servidor de aplicação separado.

---

## Limitações da Escolha

- **Multiusuário:** o Streamlit não oferece autenticação nativa. Para múltiplos usuários com dados isolados, é necessário camada adicional (proxy reverso com auth, ou biblioteca externa).
- **Interatividade:** callbacks complexos entre componentes são mais difíceis de implementar do que em Dash.
- **Performance com grandes volumes:** o modelo de re-execução do script completo a cada interação pode ser custoso. Mitigado com `@st.cache_data`.
- **Customização visual:** personalização profunda de UI requer CSS/HTML via `unsafe_allow_html`, quebrando a proposta de simplicidade.
- **Sem API:** o Streamlit não expõe os dados via REST. Para integrações externas, será necessário adicionar uma camada de API separada.

---

## Impacto Futuro na Arquitetura

A arquitetura em camadas (`domain → services → repositories`) foi projetada para ser independente da UI. Se o Streamlit se tornar insuficiente no futuro (volume de usuários, necessidade de API pública, requisitos de UX avançados), a migração para FastAPI + frontend JavaScript é viável sem reescrever a lógica de negócio.

O ponto de substituição seria apenas `app/` — as camadas `src/services/`, `src/domain/`, `src/repositories/` e `src/analytics/` permanecem intactas.

Esta decisão é **reversível sem custo alto** para as camadas internas do sistema.
