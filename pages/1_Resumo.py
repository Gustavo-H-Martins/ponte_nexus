import streamlit as st

from src.fin_dashboard.services.analytics import kpis, load_transactions

st.title("Resumo")
df = load_transactions()
stats = kpis(df)

col1, col2, col3 = st.columns(3)
col1.metric("Entradas", f"R$ {stats['incomes']:.2f}")
col2.metric("Saidas", f"R$ {stats['expenses']:.2f}")
col3.metric("Saldo", f"R$ {stats['net']:.2f}")

st.dataframe(df, use_container_width=True)
