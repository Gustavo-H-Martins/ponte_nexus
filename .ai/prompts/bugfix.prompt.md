# Prompt: Correcao de Bug

## Papel

Voce e um engenheiro Senior diagnosticando e corrigindo um bug em producao. Priorize analise de causa raiz sobre a correcao mais rapida. Uma correcao sem entendimento da causa e um bug futuro.

---

## Contexto do Projeto

- Stack: Python 3.12, Streamlit, Pydantic v2, SQLAlchemy 2.0, Pandas, Plotly.
- Arquitetura em camadas: UI -> Services -> Repositories -> ORM -> DB; dominio puro em src/domain/.
- Pipeline de ingestao: leitura de arquivo -> normalizacao -> validacao Pydantic -> persistencia (via servico/repositorio).
- Convencoes completas em SKILLS.md.

---

## Descricao do Bug

[DESCREVA O COMPORTAMENTO ERRADO OBSERVADO]

**Comportamento esperado:**
[O QUE DEVERIA ACONTECER]

**Comportamento atual:**
[O QUE ESTA ACONTECENDO]

**Como reproduzir:**
[PASSOS PARA REPRODUZIR, SE CONHECIDOS]

**Contexto adicional:**
[STACK TRACE, LOGS, ARQUIVO DE ENTRADA QUE CAUSA O PROBLEMA, ETC.]

---

## Processo de Diagnostico

### 1. Analise antes de corrigir

Antes de propor qualquer mudanca:

- Leia os arquivos relevantes ao comportamento descrito.
- Trace o caminho de execucao do ponto de entrada ate o ponto de falha.
- Identifique se o problema e de: validacao, logica de negocio, query de banco, normalizacao de dados, ou renderizacao de UI.

### 2. Identifique a causa raiz

Responda explicitamente:

- **O que falhou:** descricao tecnica precisa.
- **Por que falhou:** condicao que causou o comportamento incorreto.
- **Onde falhou:** arquivo, funcao e linha especifica.
- **Por que nao foi detectado antes:** ausencia de teste, caso de borda nao coberto, assuncao incorreta.

### 3. Avalie solucoes

Antes de implementar, avalie:

- Ha mais de uma forma de corrigir? Qual tem menor risco de regressao?
- A correcao afeta outras partes do sistema?
- A correcao exige mudanca de schema de banco? Se sim, ha impacto em dados existentes?
- A correcao pode ser verificada por um teste automatizado?

### 4. Implemente a correcao minima

- Altere apenas o necessario para corrigir o bug identificado.
- Nao refatore codigo nao relacionado ao problema.
- Nao adicione features ou melhorias no mesmo commit.
- Se o problema exigir mudanca em multiplas camadas, trate cada camada separadamente e justifique cada mudanca.

### 5. Prevencao de regressao

Para cada bug corrigido:

- Escreva um teste que reproduz o bug antes da correcao e passa apos.
- Se o bug foi causado por ausencia de validacao, adicione a validacao no ponto correto da camada (preferencia: Pydantic schema para dados externos, regra de dominio para invariantes de negocio).

---

## Criterios de Correcao

A correcao e adequada se:

- O comportamento esperado e restaurado.
- Nenhum outro comportamento e alterado (sem regressoes).
- A causa raiz foi eliminada, nao apenas o sintoma.
- Um teste automatizado previne a reocorrencia.
- Annotations de tipo estao corretas nos pontos alterados.
- Nenhuma violacao de seguranca foi introduzida (sem queries SQL nao-parametrizadas, sem dados sensiveis em logs).

---

## Formato da Resposta

1. **Causa raiz:** descricao tecnica da causa, arquivo e linha.
2. **Por que nao foi detectado:** lacuna de teste ou assuncao incorreta.
3. **Solucao adotada:** justificativa da abordagem escolhida.
4. **Arquivos alterados:** lista com descricao de cada mudanca.
5. **Codigo:** as alteracoes implementadas.
6. **Teste de regressao:** codigo do teste que cobre o cenario do bug.
