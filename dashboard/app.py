"""Dashboard PI4 — Ciência de Dados Aplicada a Situações de Mercado.

Página inicial: visão geral com KPIs e qualidade dos dados.
Execução local: ``streamlit run dashboard/app.py``
"""

import data
import streamlit as st

st.set_page_config(
    page_title="PI4 — Chocolate Sales",
    page_icon="🍫",
    layout="wide",
)

st.title("🍫 PI4 — Inteligência de Negócios | Chocolate Sales")
st.caption(
    "Projeto Integrador do 4.º semestre — Tecnólogo em Banco de Dados (SENAC EAD). "
    "Análise exploratória sobre 1 milhão de vendas de chocolate (2023–2024)."
)

st.markdown(
    "Use o menu lateral para navegar entre **Clientes**, **Produtos**, "
    "**Lojas** e **Tendências**. Esta página reúne os indicadores executivos "
    "de alto nível."
)

# --------------------------------------------------------------------------
# KPIs gerais
# --------------------------------------------------------------------------
st.header("KPIs gerais")
st.markdown(
    "Painel executivo de alto nível com receita total, margem e política de "
    "desconto, servindo como ponto de partida para avaliar saúde financeira "
    "e definir metas."
)

kpis = data.kpis_gerais()
itens = list(kpis.items())

linha1 = st.columns(3)
linha2 = st.columns(3)
for coluna, (rotulo, valor) in zip(linha1 + linha2, itens):
    coluna.metric(rotulo, valor)

st.divider()

# --------------------------------------------------------------------------
# Qualidade dos dados
# --------------------------------------------------------------------------
st.header("Qualidade dos dados")
st.markdown(
    "Valida que os dados são confiáveis antes de qualquer análise, evitando "
    "que nulos ou duplicatas distorçam métricas financeiras e induzam "
    "decisões equivocadas."
)

st.dataframe(data.qualidade_dados(), use_container_width=True)
