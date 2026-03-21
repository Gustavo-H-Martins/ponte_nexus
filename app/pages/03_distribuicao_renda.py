import streamlit as st
import plotly.express as px

from src.analytics.loader import load_transactions_df
from app.ui import page_header, plotly_layout, TYPE_COLORS, TIPO_LABEL

_TIPOS_RENDA = {"pro_labore", "dividendos"}

st.set_page_config(page_title="Minha Remuneração · Inside Money", layout="wide", page_icon="💰")


@st.cache_data(ttl=30)
def _get_data(owner_id: int | None):
    df = load_transactions_df(owner_id=owner_id)
    return df[df["transaction_type"].isin(_TIPOS_RENDA)].copy()


is_dark = page_header("Minha Remuneração", "Quanto você retirou da empresa este mês")
LAYOUT = plotly_layout(is_dark)

df = _get_data(st.session_state.get("effective_owner_id"))

if df.empty:
    st.info(
        "Nenhum pró-labore ou dividendo registrado ainda. "
        "Esses valores aparecem aqui quando você registra retiradas da empresa."
    )
    col_a, col_b, _ = st.columns([2, 2, 4])
    with col_a:
        if st.button("✏️ Registrar retirada", type="primary"):
            st.switch_page("pages/07_novo_lancamento.py")
    with col_b:
        if st.button("📂 Importar extrato"):
            st.switch_page("pages/05_importacao_dados.py")
    st.stop()

total_pro_labore = float(df.loc[df["transaction_type"] == "pro_labore", "amount"].sum())
total_dividendos = float(df.loc[df["transaction_type"] == "dividendos", "amount"].sum())

col1, col2, col3 = st.columns(3)
col1.metric("💼 Pró-Labore",       f"R$ {total_pro_labore:,.2f}")
col2.metric("💰 Dividendos",        f"R$ {total_dividendos:,.2f}")
col3.metric("∑ Total Distribuído", f"R$ {total_pro_labore + total_dividendos:,.2f}")

with st.expander("ℹ️ Pró-labore vs Dividendos — qual a diferença?", expanded=False):
    st.markdown("""
    **Pró-labore** é a remuneração mensal do sócio pelo trabalho que realiza na empresa.  
    Tem incidência de INSS e IRPF. É uma despesa dedutível da empresa.

    **Dividendos** são a distribuição dos lucros da empresa aos sócios.  
    Atualmente isentos de IR para pessoa física na maioria dos casos.  
    Dependem de que a empresa tenha lucro contabil apurado.

    **Dica:** Consulte seu contador para definir a proporção ideal para sua situação.
    """)

st.divider()

col_left, col_right = st.columns(2, gap="large")

with col_left:
    st.markdown('<span class="nx-section-label">Proporção Pró-Labore vs Dividendos</span>', unsafe_allow_html=True)
    by_type = df.groupby("transaction_type", as_index=False)["amount"].sum()
    by_type["label"] = by_type["transaction_type"].map(TIPO_LABEL).fillna(by_type["transaction_type"])
    fig2 = px.pie(
        by_type,
        names="label",
        values="amount",
        hole=0.45,
        color="label",
        color_discrete_map={"Pró-Labore": TYPE_COLORS["pro_labore"], "Dividendos": TYPE_COLORS["dividendos"]},
    )
    fig2.update_traces(textposition="inside", textinfo="percent+label")
    fig2.update_layout(**LAYOUT, showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

with col_right:
    st.markdown('<span class="nx-section-label">Evolução Mensal</span>', unsafe_allow_html=True)
    df_plot = df.copy()
    df_plot["month"] = df_plot["date"].dt.to_period("M").astype(str)
    monthly = (
        df_plot.groupby(["month", "transaction_type"], as_index=False)["amount"]
        .sum()
        .sort_values("month")
    )
    monthly["label"] = monthly["transaction_type"].map(TIPO_LABEL).fillna(monthly["transaction_type"])
    fig = px.bar(
        monthly,
        x="month",
        y="amount",
        color="label",
        barmode="group",
        color_discrete_map={"Pró-Labore": TYPE_COLORS["pro_labore"], "Dividendos": TYPE_COLORS["dividendos"]},
        labels={"amount": "R$", "month": "Mês", "label": "Tipo"},
    )
    fig.update_layout(**LAYOUT)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

st.markdown('<span class="nx-section-label">Registros</span>', unsafe_allow_html=True)
_COLS = ["date", "transaction_type", "source_entity_name", "destination_entity_name", "amount", "currency"]
cols_present = [c for c in _COLS if c in df.columns]
st.dataframe(df[cols_present], use_container_width=True, hide_index=True)
