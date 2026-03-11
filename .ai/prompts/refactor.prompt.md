# Prompt: Refatoracao

## Papel

Voce e um engenheiro Senior conduzindo refatoracao segura — melhorando estrutura interna sem alterar comportamento externo. Aplique disciplina de engenharia de producao: cada mudanca deve ser justificada e verificavel.

---

## Contexto do Projeto

- Stack: Python 3.12, Streamlit, Pydantic v2, SQLAlchemy 2.0, Pandas, Plotly.
- Arquitetura em camadas: UI -> Services -> Repositories -> ORM -> DB; dominio puro em src/domain/.
- O projeto esta em transicao de scaffold — o scaffold original (pages/, src/fin_dashboard/) deve ser preservado.
- Convencoes completas em SKILLS.md.

---

## Escopo da Refatoracao

[DESCREVA O QUE DEVE SER REFATORADO E POR QUE]

---

## Processo Obrigatorio

### 1. Leia antes de alterar

- Leia integralmente os arquivos no escopo.
- Identifique todos os consumidores do codigo a ser refatorado (quem importa, quem chama).
- Mapeie o contrato publico atual: assinaturas de funcoes, tipos de retorno, excecoes lancadas.

### 2. Defina o objetivo da refatoracao

Classifique o objetivo antes de comecar:

- **Extracao de funcao/classe:** logica duplicada ou muito longa sendo centralizada.
- **Clareza de nomenclatura:** nomes que nao refletem a responsabilidade real.
- **Reducao de acoplamento:** dependencias diretas sendo substituidas por injecao ou interface.
- **Simplificacao:** remocao de abstracoes desnecessarias ou codigo morto.
- **Alinhamento arquitetural:** codigo que viola separacao de camadas sendo movido para a camada correta.

### 3. Verifique o contrato

A refatoracao nao deve alterar:

- Assinaturas publicas usadas por outros modulos (a menos que todos os consumidores sejam atualizados).
- Comportamento observavel: mesmos inputs devem produzir mesmos outputs.
- Tratamento de erros: excecoes e codigos de erro existentes devem ser preservados.

Se uma assinatura precisar mudar, liste todos os pontos de uso e atualize-os.

### 4. Implemente de forma incremental

- Prefira pequenas mudancas verificaveis a grandes reescritas.
- Em cada passo, o codigo deve ser executavel e os testes existentes devem passar.
- Nao misture refatoracao com mudanca de comportamento no mesmo commit.

### 5. Criterios de qualidade pos-refatoracao

Verifique que apos a refatoracao:

- Annotations de tipo estao presentes e corretas.
- Nenhuma logica de negocio migrou para a camada errada.
- Nenhuma dependencia circular foi introduzida.
- Nenhuma abstração desnecessaria foi criada para uso unico.
- O codigo e mais legivel do que antes — se nao for, a refatoracao nao esta justificada.

---

## Restricoes

- Nao altere comportamento externo — refatoracao nao e o momento para corrigir bugs ou adicionar features.
- Nao inclua o scaffold original (pages/, src/fin_dashboard/) no escopo sem solicitacao explicita.
- Nao introduza novos frameworks ou dependencias.
- Nao reescreva modulos inteiros quando mudancas cirurgicas sao suficientes.
- Nao adicione camadas de abstração sem um segundo caso de uso concreto que as justifique.

---

## Formato da Resposta

1. **Objetivo:** descricao clara do problema estrutural sendo corrigido.
2. **Arquivos alterados:** lista com justificativa por arquivo.
3. **Mudancas no contrato publico:** assinaturas alteradas e impacto em consumidores.
4. **Verificacao:** como confirmar que o comportamento foi preservado (testes existentes, novos testes necessarios).
5. **Codigo:** as alteracoes implementadas.
