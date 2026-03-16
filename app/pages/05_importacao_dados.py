import io

import pandas as pd
import streamlit as st

from src.services.ingestion_service import create_ingestion_service
from app.ui import page_header, feather_icon

st.set_page_config(page_title="Importar Extrato · Ponte Nexus", layout="wide", page_icon="📂", initial_sidebar_state="collapsed")

page_header("Importar Extrato", "Importe o extrato do seu banco ou planilha")

with st.expander("\u2139\ufe0f Como preparar seu arquivo para importação", expanded=False):
    st.markdown("""
    **Dica de ouro:** A forma mais fácil é copiar o extrato do seu banco no formato CSV e ajustar os nomes das colunas.

    O arquivo precisa ter exatamente estes cabeçalhos (linha 1):  
    `id_lancamento`, `data`, `tipo_entidade`, `nome_entidade`, `tipo_transacao`, `categoria`, `descricao`, `valor`, `moeda`, `conta_origem`, `conta_destino`

    **Tipos de transação aceitos:**  
    `receita` | `despesa` | `transferencia_pf_pj` | `transferencia_pj_pf` | `aporte_pf_pj` | `emprestimo_pf_pj` | `dividendos` | `pro_labore`

    **Formato de data:** YYYY-MM-DD (ex: 2026-01-15)

    """)
    _sample_path = Path(__file__).resolve().parents[2] / "data" / "samples" / "sample_valid.csv"
    if _sample_path.exists():
        st.download_button(
            label=f"{feather_icon('download', 18)} Baixar modelo (sample_valid.csv)",
            data=_sample_path.read_bytes(),
            file_name="modelo_importacao.csv",
            mime="text/csv",
        )

st.markdown(
    """
**Colunas obrigatórias** — o arquivo deve conter exatamente estes nomes de cabeçalho:

| Coluna | Formato | Descrição |
|---|---|---|
| `id_lancamento` | texto | Identificador único do lançamento |
| `data` | YYYY-MM-DD | Data da transação |
| `tipo_entidade` | `PF` ou `PJ` | Tipo da entidade principal |
| `nome_entidade` | texto | Nome da entidade principal |
| `tipo_transacao` | ver abaixo | Tipo do fluxo financeiro |
| `categoria` | texto | Categoria do lançamento |
| `descricao` | texto | Descrição livre |
| `valor` | decimal > 0 | Valor da transação |
| `moeda` | 3 letras | Código da moeda (ex: `BRL`) |
| `conta_origem` | texto | Conta de origem |
| `conta_destino` | texto | Conta de destino |

Coluna opcional: `nome_contraparte` — entidade de contraparte em fluxos cruzados PF↔PJ.

**Valores válidos para `tipo_transacao`:**

`receita` · `despesa` · `transferencia_pf_pj` · `transferencia_pj_pf` ·
`aporte_pf_pj` · `emprestimo_pf_pj` · `dividendos` · `pro_labore`
"""
)

uploaded_file = st.file_uploader(
    "Selecione o arquivo",
    type=["csv", "xlsx", "json"],
    accept_multiple_files=False,
)

if uploaded_file is None:
    st.stop()

file_bytes = uploaded_file.getvalue()
ext = uploaded_file.name.rsplit(".", 1)[-1].lower()

# Preview
st.markdown('<span class="nx-section-label">Pré-visualização</span>', unsafe_allow_html=True)
try:
    if ext == "csv":
        preview_df = pd.read_csv(io.StringIO(file_bytes.decode("utf-8")))
    elif ext == "xlsx":
        preview_df = pd.read_excel(io.BytesIO(file_bytes))
    else:
        preview_df = pd.read_json(io.StringIO(file_bytes.decode("utf-8")))
    st.dataframe(preview_df.head(10), use_container_width=True, hide_index=True)
    st.caption(f"{len(preview_df)} linha(s) detectada(s).")
except Exception as exc:
    st.error(f"Não foi possível ler o arquivo: {exc}")
    st.stop()

# Importar
if st.button("Importar", type="primary"):
    with st.spinner("Validando e importando..."):
        service = create_ingestion_service()
        result = service.ingest_upload(uploaded_file.name, file_bytes)

    if result["status"] == "failed":
        st.error(
            f"Importação falhou — {result['records_total']} registros analisados, "
            f"{len(result['errors'])} erro(s) encontrado(s)."
        )
        for err in result["errors"][:20]:
            st.warning(
                f"Linha {err.get('row_number', '?')} | "
                f"Campo: {err.get('field_name', '?')} | "
                f"{err.get('error_message', '')}"
            )
        if len(result["errors"]) > 20:
            st.caption(f"… e mais {len(result['errors']) - 20} erros não exibidos.")
    else:
        n_inserted = result['records_inserted']
        n_skipped  = result['records_skipped']
        st.toast(f"✅ {n_inserted} registro(s) importado(s) com sucesso!", icon="✅")
        st.success(
            f"Concluído: {n_inserted} registro(s) inserido(s), "
            f"{n_skipped} ignorado(s) (já existiam)."
        )
        st.cache_data.clear()
        if st.button("📋 Ver no extrato", type="primary"):
            st.switch_page("pages/06_lancamentos.py")
