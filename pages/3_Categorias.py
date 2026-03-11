import plotly.express as px
import streamlit as st

from src.fin_dashboard.services.analytics import load_transactions

st.title("Categorias")
df = load_transactions()

if df.empty:
    st.warning("Sem dados para exibir.")
else:
    by_cat = df.groupby("category", as_index=False)["amount"].sum().sort_values("amount", ascending=False)
    fig = px.pie(by_cat, names="category", values="amount")
    st.plotly_chart(fig, use_container_width=True)
