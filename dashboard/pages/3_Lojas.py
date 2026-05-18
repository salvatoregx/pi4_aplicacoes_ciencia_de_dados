"""Página Lojas: desempenho por loja, tiers e comparação entre cidades."""

import data
import streamlit as st

st.set_page_config(page_title="Lojas — PI4", page_icon="🏬", layout="wide")

st.title("🏬 Lojas")

# --------------------------------------------------------------------------
st.header("Desempenho das lojas")
st.markdown(
    "Classifica unidades em tiers para priorizar recursos, identificar "
    "referências operacionais e sinalizar onde intervir."
)

lojas = data.desempenho_lojas()

# Distribuição das lojas por tier de desempenho.
contagem_tiers = lojas["tier_desempenho"].value_counts()
colunas = st.columns(len(contagem_tiers))
for coluna, (tier, quantidade) in zip(colunas, contagem_tiers.items()):
    coluna.metric(tier, f"{quantidade} lojas")

filtro = st.multiselect(
    "Filtrar por tier de desempenho",
    options=lojas["tier_desempenho"].unique().tolist(),
    default=lojas["tier_desempenho"].unique().tolist(),
)
st.dataframe(
    lojas[lojas["tier_desempenho"].isin(filtro)], use_container_width=True
)

st.divider()

# --------------------------------------------------------------------------
st.header("Desempenho por cidade")
st.markdown(
    "Compara receita, lucro e volume de vendas entre cidades, permitindo à "
    "gestão identificar quais praças geram mais valor e onde concentrar "
    "investimentos em expansão ou ações corretivas em unidades de baixo "
    "retorno."
)
st.plotly_chart(data.figura_cidade(), use_container_width=True)
