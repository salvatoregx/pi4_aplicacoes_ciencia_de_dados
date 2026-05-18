"""Página Tendências: evolução temporal, sazonalidade e clusters."""

import data
import streamlit as st

st.set_page_config(page_title="Tendências — PI4", page_icon="📈", layout="wide")

st.title("📈 Tendências")

# --------------------------------------------------------------------------
st.header("Desempenho mensal de vendas")
st.markdown(
    "Monitoria de receita e lucro com crescimento MoM; a queda recorrente em "
    "fevereiro nos dois anos é um sinal acionável para campanhas promocionais "
    "sazonais."
)
mensal = data.desempenho_mensal()
mensal_grafico = mensal.assign(
    periodo=mensal["ano"].astype(str) + "-" + mensal["mes"].astype(str).str.zfill(2)
)
st.line_chart(mensal_grafico, x="periodo", y=["receita_total", "lucro_total"])
st.dataframe(mensal, use_container_width=True)

st.divider()

# --------------------------------------------------------------------------
st.header("Sazonalidade Year-over-Year")
st.markdown(
    "Separa variação sazonal de tendência real, mais robusto que MoM para "
    "planejamento de médio prazo e definição de quando lançar produtos ou "
    "promover."
)
pivot_yoy, estatisticas_yoy = data.sazonalidade_yoy()
st.dataframe(pivot_yoy, use_container_width=True)

colunas = st.columns(3)
for coluna, (rotulo, valor) in zip(colunas * 2, estatisticas_yoy.items()):
    coluna.metric(rotulo, valor)

st.divider()

# --------------------------------------------------------------------------
st.header("Vendas por estação do ano")
st.markdown(
    "Revela a flutuação sazonal dos 10 produtos mais vendidos. Permite "
    "antecipar picos e quedas de demanda para ajustar estoque, negociar com "
    "fornecedores e planejar campanhas promocionais alinhadas ao calendário "
    "de consumo."
)
st.plotly_chart(data.figura_estacao(), use_container_width=True)

st.divider()

# --------------------------------------------------------------------------
st.header("Consumo por dia da semana")
st.markdown(
    "Segmenta o consumo por dia da semana, gênero e faixa etária. Identifica "
    "os dias de maior e menor movimento e quais perfis demográficos os "
    "impulsionam, orientando decisões de escala de equipe, promoções "
    "direcionadas e horário de funcionamento."
)
st.plotly_chart(data.figura_dia_semana(), use_container_width=True)

st.divider()

# --------------------------------------------------------------------------
st.header("Tendência diária de receita e volume")
st.markdown(
    "Acompanha receita e volume de vendas diários com médias móveis de 14 "
    "dias, suavizando flutuações pontuais para evidenciar tendências reais e "
    "padrões sazonais que orientem planejamento de estoque e campanhas."
)
st.plotly_chart(data.figura_tendencia_diaria(), use_container_width=True)

st.divider()

# --------------------------------------------------------------------------
st.header("Clusterização de clientes")
st.markdown(
    "Agrupa clientes em 4 perfis comportamentais via K-Means, visualizados "
    "por PCA. Cada cluster representa um arquétipo de consumidor com padrões "
    "distintos de gênero, idade, dia preferido e sazonalidade, viabilizando "
    "campanhas de marketing segmentadas e personalizadas."
)
figura_pca, figura_comportamento, distribuicao_clusters = data.clusterizacao()
st.plotly_chart(figura_pca, use_container_width=True)

st.subheader("Distribuição dos clusters")
st.dataframe(
    distribuicao_clusters.rename("quantidade"),
    use_container_width=True,
)

st.subheader("Comportamento dos clusters por dia da semana")
st.markdown(
    "Detalha o volume de compras de cada perfil de cluster ao longo da "
    "semana. Torna visível quando cada segmento é mais ativo, permitindo "
    "ações promocionais no momento certo para o público certo."
)
st.plotly_chart(figura_comportamento, use_container_width=True)

st.divider()

# --------------------------------------------------------------------------
st.header("Relação entre receita e lucro")
st.markdown(
    "Visualiza a relação entre receita e lucro por venda com linha de "
    "tendência e correlação. Permite identificar se o crescimento de receita "
    "é acompanhado por aumento proporcional no lucro, sinalizando eficiência "
    "operacional e boa gestão de custos, além de evidenciar possíveis "
    "distorções que demandem ação corretiva."
)
figura_receita_lucro, correlacao_receita_lucro = data.receita_lucro()
st.plotly_chart(figura_receita_lucro, use_container_width=True)

colunas = st.columns(2)
for coluna, (rotulo, valor) in zip(colunas, correlacao_receita_lucro.items()):
    coluna.metric(rotulo, valor) 
