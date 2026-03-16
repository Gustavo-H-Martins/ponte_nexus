import streamlit as st

from app.ui import page_header

st.set_page_config(page_title="Como Usar · Ponte Nexus", layout="wide", page_icon="💠")

page_header("Como Usar", "Guia rápido para tirar o máximo do Ponte Nexus")

# ── Sumário de navegação ──────────────────────────────────────────────────────
st.markdown("""
**Ir direto para:**  
[Primeiros passos](#primeiros-passos) · [Importar extrato](#importar-extrato) ·
[Registrar transação](#registrar-transacao) · [Entender os relatórios](#entender-os-relatorios) ·
[FAQ](#perguntas-frequentes)
""")

st.divider()

# ── 1. Primeiros passos ────────────────────────────────────────────────────────
st.markdown("## 🚀 Primeiros passos")
st.markdown("""
Quando você abre o Ponte Nexus pela primeira vez, o sistema guia você por 4 etapas:

**1. Criar seu perfil pessoal (Pessoa Física)**  
Informe seu nome. Isso cria sua identidade no sistema para separar finanças pessoais das empresariais.

**2. Adicionar sua empresa (opcional)**  
Se você tem CNPJ (MEI, LTDA, S.A. etc.), cadastre sua empresa. Isso permite analisar o fluxo de dinheiro
entre você e a empresa.

**3. Cadastrar fontes de renda**  
Adicione de onde vem seu dinheiro: salário, freelance, dividendos da empresa, aluguel. Com isso, o
sistema consegue mostrar qual fonte contribui mais para sua renda.

**4. Adicionar seus dados**  
Importe um extrato bancário (CSV/XLSX/JSON) ou registre sua primeira transação manualmente.
""")

with st.expander("💡 Posso pular algum passo?", expanded=False):
    st.markdown("""
    Sim. Os passos 2 (empresa) e 3 (fontes de renda) podem ser pulados.
    Você pode voltar a configurá-los a qualquer momento pelo menu **Fontes de Renda**.

    O passo 1 (perfil pessoal) é obrigatório para que o sistema funcione corretamente.
    """)

st.divider()

# ── 2. Importar extrato ────────────────────────────────────────────────────────
st.markdown("## 📂 Como importar seu extrato bancário")
st.markdown("""
Acesse **Importar Extrato** no menu lateral e siga os passos:

1. Exporte o extrato do seu banco em formato **CSV**, **XLSX** ou **JSON**.
2. Abra o arquivo e renomeie as colunas para os nomes esperados pelo sistema.
3. Faça o upload do arquivo e confira a pré-visualização.
4. Clique em **Importar** — o sistema valida cada linha e mostra os erros encontrados.

**Colunas obrigatórias do arquivo:**

| Coluna | Exemplo |
|---|---|
| `id_lancamento` | `TRX-001` |
| `data` | `2026-01-15` |
| `tipo_entidade` | `PF` ou `PJ` |
| `nome_entidade` | `João Silva` |
| `tipo_transacao` | `receita`, `despesa`, `dividendos`… |
| `categoria` | `Alimentação` |
| `descricao` | `Supermercado Pão de Açúcar` |
| `valor` | `350.00` |
| `moeda` | `BRL` |
| `conta_origem` | `Conta Corrente PF` |
| `conta_destino` | `Conta Corrente PF` |
""")

_sample_path = Path(__file__).resolve().parents[2] / "data" / "samples" / "sample_valid.csv"
if _sample_path.exists():
    st.download_button(
        label="⬇️ Baixar arquivo de exemplo (modelo_importacao.csv)",
        data=_sample_path.read_bytes(),
        file_name="modelo_importacao.csv",
        mime="text/csv",
    )

with st.expander("💡 Quais tipos de transação posso usar?", expanded=False):
    st.markdown("""
    | Tipo | Quando usar |
    |---|---|
    | `receita` | Qualquer valor que entrou (salário, pagamento de cliente) |
    | `despesa` | Qualquer valor que saiu (compras, contas, impostos) |
    | `pro_labore` | Retirada mensal sua como sócio-administrador |
    | `dividendos` | Distribuição de lucros da empresa para você |
    | `aporte_pf_pj` | Dinheiro que você colocou na empresa como capital |
    | `emprestimo_pf_pj` | Dinheiro que você emprestou para a empresa |
    | `transferencia_pf_pj` | Transferência genérica de você para a empresa |
    | `transferencia_pj_pf` | Transferência genérica da empresa para você |
    """)

st.divider()

# ── 3. Registrar transação ────────────────────────────────────────────────────
st.markdown("## ✏️ Como registrar uma transação manualmente")
st.markdown("""
Acesse **Registrar Transação** no menu lateral.

Antes de registrar, certifique-se de ter cadastrado:
- Ao menos uma **entidade** (seu perfil PF ou sua empresa PJ)
- Ao menos uma **conta** vinculada a essa entidade
- Ao menos uma **categoria** (ex: Alimentação, Transporte, Salário)

Se ainda não tem esses cadastros, vá para a aba **⚙️ Configurações** dentro da própria tela de registro.

**Passo a passo:**
1. Selecione o tipo de entidade (**PF** ou **PJ**) e o nome
2. Escolha a conta de origem e a conta de destino
3. Informe a data, tipo de transação, categoria e valor
4. Clique em **Salvar lançamento**
""")

with st.expander("💡 Quando usar 'Receita' vs 'Transferência'?", expanded=False):
    st.markdown("""
    **Receita** → Dinheiro novo que entrou no seu patrimônio. Ex: salário recebido, pagamento de um cliente.

    **Transferência PF↔PJ** → Dinheiro que já era seu, mas mudou de "bolso".
    Ex: você transferiu R$ 5.000 da sua conta pessoal para a conta da empresa — o dinheiro não entrou nem saiu do seu patrimônio total,
    apenas mudou de lugar.

    **Regra de ouro:** Se o dinheiro veio de fora (cliente, empregador, banco), é **receita**.
    Se veio de outra conta sua, é **transferência**.
    """)

st.divider()

# ── 4. Entender os relatórios ─────────────────────────────────────────────────
st.markdown("## 📊 Como interpretar os relatórios")

col_left, col_right = st.columns(2, gap="large")

with col_left:
    st.markdown("**🏠 Meu Bolso (Finanças Pessoais)**")
    st.markdown("""
    Mostra sua situação financeira como **pessoa física**:
    - Quanto você recebeu (pró-labore + dividendos + outras receitas PF)
    - Quanto gastou em despesas pessoais
    - Seu saldo pessoal do mês
    - Comparação com o mês anterior
    """)

    st.markdown("**💰 Minha Remuneração**")
    st.markdown("""
    Quanto você retirou da empresa no período, separado entre pró-labore e dividendos.
    Útil para acompanhar se sua remuneração está crescendo ou estável.
    """)

    st.markdown("**🌱 Fontes de Renda**")
    st.markdown("""
    Ranking das suas fontes de renda: qual empresa, cliente ou ativo contribuiu mais.
    Ideal para visualizar dependência de uma única fonte.
    """)

with col_right:
    st.markdown("**📊 Visão Geral (Dashboard)**")
    st.markdown("""
    Resumo de todos os fluxos do período: receitas PJ, receitas PF, despesas e saldo.
    Inclui comparação automática com o mês anterior quando há dados disponíveis.
    """)

    st.markdown("**🔄 Transferências**")
    st.markdown("""
    Visualiza todo o dinheiro que circulou entre você e sua empresa.
    Mostra quanto foi de você para a empresa e quanto voltou.
    """)

    st.markdown("**🎯 Orçamento**")
    st.markdown("""
    Defina limites de gastos mensais por categoria e acompanhe quanto já foi usado.
    Alertas visuais aparecem quando você se aproxima ou ultrapassa o limite.
    """)

st.divider()

# ── 5. FAQ ─────────────────────────────────────────────────────────────────────
st.markdown("## ❓ Perguntas frequentes")

with st.expander("Por que o dashboard está em branco?"):
    st.markdown("""
    O sistema precisa de pelo menos uma transação cadastrada para exibir gráficos.
    Se você acabou de configurar o perfil, importe um extrato ou registre sua primeira transação.
    """)

with st.expander("Posso ter mais de uma empresa cadastrada?"):
    st.markdown("""
    Sim. Cadastre quantas empresas precisar em **Registrar Transação → ⚙️ Configurações**.
    Cada empresa aparece separadamente nos gráficos de análise.
    """)

with st.expander("O que fazer se o arquivo de importação retornar erros?"):
    st.markdown("""
    O sistema mostra exatamente qual linha e qual campo causou o problema.
    Os erros mais comuns são:
    - Coluna com nome errado (verifique espaços extras e maiúsculas/minúsculas)
    - Tipo de transação não reconhecido (use exatamente os valores da tabela)
    - Data no formato errado (use YYYY-MM-DD)
    - Valor negativo ou zero (o sistema espera apenas valores positivos)
    """)

with st.expander("Meus dados ficam salvos onde?"):
    st.markdown("""
    Os dados ficam armazenados localmente em um banco SQLite no diretório `data/` do projeto.
    Não há envio de dados para servidores externos. Sua privacidade financeira é preservada.
    """)

with st.expander("Como funciona o orçamento por categoria?"):
    st.markdown("""
    Acesse **Orçamento** no menu lateral.
    1. Selecione uma categoria (ex: Alimentação)
    2. Defina um valor limite para o mês
    3. O sistema calcula automaticamente quanto já foi gasto nessa categoria no período
    4. Uma barra de progresso mostra o percentual utilizado

    Alertas aparecem em laranja quando você atinge 70% e em vermelho quando ultrapassa 90%.
    """)
