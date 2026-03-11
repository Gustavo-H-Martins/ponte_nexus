import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd
import streamlit as st

from src.services.ingestion_service import create_ingestion_service

st.title("Importacao de Dados")

st.markdown(
    """
Formatos aceitos: **CSV**, **XLSX**, **JSON**

**Colunas obrigatorias:**

| Coluna | Formato | Descricao |
|---|---|---|
| transaction_id | texto | Identificador unico |
| date | YYYY-MM-DD | Data da transacao |
| entity_type | PF ou PJ | Tipo da entidade |
| entity_name | texto | Nome da entidade |
| transaction_type | texto | Tipo do fluxo |
| category | texto | Categoria |
| description | texto | Descricao |
| amount | decimal > 0 | Valor |
| currency | 3 letras | Moeda (ex: BRL) |
| source_account | texto | Conta de origem |
| destination_account | texto | Conta de destino |

Coluna opcional: `counter_entity_name` (contraparte em fluxos cruzados PF<->PJ).

**Tipos validos:** `income`, `expense`, `transfer_pf_to_pj`, `transfer_pj_to_pf`,
`investment_pf_to_pj`, `loan_pf_to_pj`, `dividend_distribution`, `pro_labore`
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
st.subheader("Preview")
try:
    if ext == "csv":
        preview_df = pd.read_csv(io.StringIO(file_bytes.decode("utf-8")))
    elif ext == "xlsx":
        preview_df = pd.read_excel(io.BytesIO(file_bytes))
    else:
        preview_df = pd.read_json(io.StringIO(file_bytes.decode("utf-8")))
    st.dataframe(preview_df.head(10), use_container_width=True)
    st.caption(f"{len(preview_df)} linhas detectadas.")
except Exception as exc:
    st.error(f"Nao foi possivel ler o arquivo: {exc}")
    st.stop()

# Importar
if st.button("Importar", type="primary"):
    with st.spinner("Validando e importando..."):
        service = create_ingestion_service()
        result = service.ingest_upload(uploaded_file.name, file_bytes)

    if result["status"] == "failed":
        st.error(
            f"Importacao falhou — {result['records_total']} registros analisados, "
            f"{len(result['errors'])} erro(s) encontrado(s)."
        )
        for err in result["errors"][:20]:
            st.warning(
                f"Linha {err.get('row_number', '?')} | "
                f"Campo: {err.get('field_name', '?')} | "
                f"{err.get('error_message', '')}"
            )
        if len(result["errors"]) > 20:
            st.caption(f"... e mais {len(result['errors']) - 20} erros nao exibidos.")
    else:
        st.success(
            f"Concluido: {result['records_inserted']} registros inseridos, "
            f"{result['records_skipped']} ignorados (ja existiam)."
        )
        st.cache_data.clear()
