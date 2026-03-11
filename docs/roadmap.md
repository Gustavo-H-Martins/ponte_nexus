# Roadmap

Este documento registra melhorias planejadas e possíveis evoluções do sistema.

---

## Em Desenvolvimento

### Migração do scaffold original para o novo

O scaffold legado (`pages/`, `src/fin_dashboard/`, `streamlit_app.py` raiz) existe para compatibilidade durante a transição. A migração completa para o novo scaffold (`app/`, `src/` com camadas DDD) precisa ser finalizada antes de qualquer refatoração arquitetural mais ampla.

**Critério de conclusão:** remoção segura de `pages/` e `src/fin_dashboard/` sem perda de funcionalidade.

---

## Melhorias de Curto Prazo

### Migrações de banco com Alembic

Atualmente o schema é criado via `Base.metadata.create_all()`, que não aplica alterações em tabelas existentes. A configuração do Alembic permitirá evoluir o schema com segurança em ambientes com dados persistidos.

### Cobertura de testes

Aumentar cobertura das camadas de repositório e serviço. Adicionar testes de contrato para o schema de validação com casos de borda (valores negativos, datas inválidas, enums desconhecidos).

### Validação de direção PF↔PJ na ingestão

`validate_flow_direction()` em `src/domain/rules.py` existe mas ainda não é chamado durante o pipeline de ingestão. Integrar essa validação no `IngestionService`.

### Paginação na página de Lançamentos

A tabela de lançamentos carrega todos os registros em memória. Para volumes grandes, implementar paginação via `st.dataframe` com `use_container_width` e filtragem server-side antes do carregamento.

---

## Melhorias de Médio Prazo

### Filtros globais de período

Implementar um seletor de período global na barra lateral que persista via `st.session_state` e seja compartilhado entre todas as páginas analíticas.

### Suporte a múltiplas moedas

Atualmente o sistema persiste a moeda por transação mas não faz conversão. Adicionar suporte a conversão via taxa de câmbio configurável para consolidar valores em BRL.

### Autenticação

O Streamlit não oferece autenticação nativa. Para ambientes multi-usuário, avaliar `streamlit-authenticator` ou proxy reverso com autenticação (ex: Nginx + OAuth2 Proxy).

### Exportação de relatório consolidado

Expandir `app/export.py` para gerar um relatório PDF com todas as páginas analíticas em formato de relatório gerencial mensal.

---

## Evoluções de Arquitetura

### API REST como backend opcional

Separar a camada de serviço em uma API FastAPI independente, permitindo que o Streamlit (ou outra interface) consuma os dados via HTTP. Isso facilitaria integrações externas e testes de integração mais isolados.

### Cache distribuído

Para implantações com múltiplos workers Streamlit, substituir o `@st.cache_data` por cache externo (Redis) para consistência entre instâncias.

### Suporte a PostgreSQL em desenvolvimento

Tornar o ambiente de desenvolvimento mais próximo da produção com Docker Compose configurado com PostgreSQL + pgAdmin.

### Agendamento de relatórios

Adicionar suporte a geração automática de relatórios periódicos (mensais/trimestrais) via APScheduler ou integração com ferramentas de orquestração (Prefect, Airflow).

---

## Funcionalidades Planejadas

| Funcionalidade | Prioridade | Notas |
|---|---|---|
| Alembic para migrações | Alta | Necessário antes de qualquer deploy em produção |
| Validação de direção PF↔PJ na ingestão | Alta | Regra já existe, precisa ser integrada |
| Filtros globais de período | Média | Melhora significativa na UX |
| Suporte a múltiplas moedas | Média | Requer decisão sobre fonte de câmbio |
| API REST (FastAPI) | Baixa | Dependente de requisito de integração |
| Autenticação | Baixa | Dependente de requisito de multi-usuário |
