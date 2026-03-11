# Ingestão de Dados

## Visão Geral

O sistema aceita arquivos nos formatos **CSV**, **XLSX** e **JSON**. O formato é detectado automaticamente pela extensão do arquivo.

O pipeline de ingestão executa três etapas em sequência:

```
Arquivo → Reader → Normalizer → Validator → Persistência
```

Se qualquer linha falhar na validação, **toda a importação é rejeitada**. O sistema retorna a lista de erros por linha para correção antes de uma nova tentativa.

---

## Schema Esperado

Todos os arquivos devem conter as seguintes colunas com exatamente estes nomes:

| Coluna | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `id_lancamento` | texto | sim | Identificador único do lançamento. Usado para deduplicação. |
| `data` | YYYY-MM-DD | sim | Data da transação |
| `tipo_entidade` | `PF` ou `PJ` | sim | Tipo da entidade principal do lançamento |
| `nome_entidade` | texto | sim | Nome da entidade principal |
| `tipo_transacao` | ver tabela abaixo | sim | Tipo do fluxo financeiro |
| `categoria` | texto | sim | Categoria do lançamento |
| `descricao` | texto | sim | Descrição livre (pode ser string vazia) |
| `valor` | decimal > 0 | sim | Valor da transação. Deve ser positivo. |
| `moeda` | 3 caracteres | sim | Código ISO da moeda (ex: `BRL`, `USD`) |
| `conta_origem` | texto | sim | Nome da conta de origem |
| `conta_destino` | texto | sim | Nome da conta de destino |
| `nome_contraparte` | texto | não | Entidade de contraparte em fluxos cruzados PF↔PJ |

---

## Tipos de Transação

| Valor | Direção |
|---|---|
| `receita` | entrada na PJ |
| `despesa` | saída da PJ |
| `transferencia_pf_pj` | PF → PJ |
| `transferencia_pj_pf` | PJ → PF |
| `aporte_pf_pj` | PF → PJ |
| `emprestimo_pf_pj` | PF → PJ |
| `dividendos` | PJ → PF |
| `pro_labore` | PJ → PF |

---

## Tolerâncias de Normalização

O pipeline normaliza automaticamente antes de validar:

- Nomes de colunas: espaços extras são removidos.
- `moeda`: convertido para maiúsculo e sem espaços (`brl` → `BRL`).
- `tipo_entidade`: convertido para maiúsculo (`pf` → `PF`).
- `tipo_transacao`: convertido para minúsculo (`Receita` → `receita`).
- `nome_contraparte`: `NaN` e strings em branco são convertidos para `null`.

---

## Formatos de Arquivo

### CSV

- Separador: vírgula (`,`)
- Encoding: UTF-8
- Cabeçalho na primeira linha

Exemplo:

```csv
id_lancamento,data,tipo_entidade,nome_entidade,tipo_transacao,categoria,descricao,valor,moeda,conta_origem,conta_destino,nome_contraparte
TXN-001,2024-01-15,PJ,Empresa Alpha,receita,Serviços,Consultoria jan/24,15000.00,BRL,Conta PJ,Conta PJ,
TXN-002,2024-01-31,PJ,Empresa Alpha,pro_labore,Remuneração,Pró-labore jan/24,5000.00,BRL,Conta PJ,Conta PF João Silva,João Silva
```

### XLSX

- Cabeçalho na linha 1 com os nomes exatos das colunas.
- Uma aba (sheet) com os dados. O reader usa a primeira aba.
- Valores de data devem ser do tipo Date no Excel ou string no formato `YYYY-MM-DD`.

### JSON

Array de objetos, onde cada objeto representa um lançamento:

```json
[
  {
    "id_lancamento": "TXN-001",
    "data": "2024-01-15",
    "tipo_entidade": "PJ",
    "nome_entidade": "Empresa Alpha",
    "tipo_transacao": "receita",
    "categoria": "Serviços",
    "descricao": "Consultoria jan/24",
    "valor": 15000.00,
    "moeda": "BRL",
    "conta_origem": "Conta PJ",
    "conta_destino": "Conta PJ",
    "nome_contraparte": null
  }
]
```

---

## Comportamento em Caso de Erros

Quando a validação falha, o sistema retorna:

```json
{
  "status": "failed",
  "records_total": 50,
  "records_valid": 0,
  "records_inserted": 0,
  "records_skipped": 0,
  "errors": [
    {
      "row_number": 3,
      "field_name": "valor",
      "error_code": "greater_than",
      "error_message": "Input should be greater than 0"
    }
  ]
}
```

A UI exibe os primeiros 20 erros com número de linha e campo. Corrija os erros no arquivo e refaça o upload.

---

## Deduplicação

O campo `id_lancamento` é persistido como `external_transaction_id` com constraint `UNIQUE` no banco. Registros com `id_lancamento` já existente são ignorados silenciosamente (`records_skipped`), sem causar erro.

---

## Arquivo de Exemplo

Um arquivo CSV válido está disponível em `data/samples/sample_valid.csv` para referência e testes.
