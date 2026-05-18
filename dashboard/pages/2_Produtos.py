"""Página Produtos: intensidade de cacau, categorias e descontos."""

import data
import streamlit as st

st.set_page_config(page_title="Produtos — PI4", page_icon="🍫", layout="wide")

st.title("🍫 Produtos")

# --------------------------------------------------------------------------
st.header("Produtos por intensidade de cacau")
st.markdown(
    "Orienta decisões de mix: quais categorias e percentuais de cacau são "
    "mais rentáveis, o que priorizar em gôndola e o que pode ser "
    "descontinuado."
)
df_produtos, metricas_cacau = data.produtos_cacau()

col_a, col_b = st.columns(2)
with col_a:
    st.subheader("Lucro e volume por intensidade")
    st.dataframe(metricas_cacau, use_container_width=True)
with col_b:
    st.subheader("Detalhe por categoria e % de cacau")
    st.dataframe(df_produtos, use_container_width=True)

st.divider()

# --------------------------------------------------------------------------
st.header("Desempenho por categoria de produto")
st.markdown(
    "Agrega lucro e volume de vendas por categoria de produto, oferecendo "
    "uma visão consolidada de quais linhas são mais rentáveis e onde "
    "concentrar esforços comerciais."
)
desempenho_categoria = (
    df_produtos.groupby("category")[["lucro_total", "volume_total"]]
    .sum()
    .reset_index()
    .sort_values("lucro_total", ascending=False)
)
st.dataframe(desempenho_categoria, use_container_width=True)
st.bar_chart(desempenho_categoria, x="category", y="lucro_total")

st.divider()

# --------------------------------------------------------------------------
st.header("Descontos")
st.markdown(
    "Quantifica o trade-off entre volume e margem por faixa de desconto, com "
    "correlação e impacto em pontos percentuais como evidência objetiva para "
    "revisar a política."
)
df_faixas, correlacao = data.impacto_desconto()

st.subheader("Métricas por faixa de desconto")
st.dataframe(df_faixas, use_container_width=True)

st.subheader("Correlação e impacto")
colunas = st.columns(3)
for coluna, (rotulo, valor) in zip(colunas * 2, correlacao.items()):
    coluna.metric(rotulo, valor)
