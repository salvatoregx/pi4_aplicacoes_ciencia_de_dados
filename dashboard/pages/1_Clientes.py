"""Página Clientes: segmentação, preferências por gênero e fidelidade."""

import data
import streamlit as st

st.set_page_config(page_title="Clientes — PI4", page_icon="👥", layout="wide")

st.title("👥 Clientes")
st.markdown(
    "Direciona campanhas e programas de fidelidade; verifica se o loyalty "
    "diferencia comportamento de compra e se gênero implica preferências "
    "distintas de produto."
)

# --------------------------------------------------------------------------
st.header("Segmentação por faixa etária e fidelidade")
st.markdown(
    "Gasto médio, gasto total e número de clientes em cada cruzamento de "
    "faixa etária com status de membro do programa de fidelidade."
)
st.dataframe(data.segmentacao_clientes(), use_container_width=True)

st.divider()

# --------------------------------------------------------------------------
st.header("Preferências por gênero")
df_categoria, df_cacau = data.preferencias_genero()

aba_cat, aba_cacau = st.tabs(["Por categoria de produto", "Por intensidade de cacau"])
with aba_cat:
    st.markdown(
        "Participação de cada categoria na receita dentro de cada gênero."
    )
    st.dataframe(df_categoria, use_container_width=True)
with aba_cacau:
    st.markdown(
        "Participação de cada faixa de intensidade de cacau na receita "
        "dentro de cada gênero."
    )
    st.dataframe(df_cacau, use_container_width=True)

st.divider()

# --------------------------------------------------------------------------
st.header("Fidelidade")
st.markdown(
    "Contrasta ticket médio e frequência de compras entre membros do "
    "programa de fidelidade e não-membros. Se o programa não gera diferença "
    "significativa de comportamento, a empresa pode reavaliar o investimento "
    "ou redesenhar os benefícios oferecidos."
)
st.plotly_chart(data.figura_fidelidade(), use_container_width=True)