import plotly.express as px
import streamlit as st

from src.fin_dashboard.services.analytics import load_transactions

st.title("Fluxo de Caixa")
df = load_transactions()

if df.empty:
    st.warning("Sem dados para exibir.")
else:
    grouped = (
        df.assign(occurred_on=lambda x: x["occurred_on"].astype(str))
        .groupby(["occurred_on", "tx_type"], as_index=False)["amount"]
        .sum()
    )
    fig = px.bar(grouped, x="occurred_on", y="amount", color="tx_type", barmode="group")
    st.plotly_chart(fig, use_container_width=True)
