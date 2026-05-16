"""Camada de acesso a dados e gráficos do dashboard.

Reaproveita as análises herdadas da 1.ª etapa (``src/analysis.py``) sem
alterá-las e usa as visualizações Plotly de ``charts.py``. Todo resultado
pesado é memorizado com o cache do Streamlit para evitar reprocessar
1 milhão de linhas a cada navegação entre páginas.
"""

import sys
from pathlib import Path

import streamlit as st

# Torna o pacote src/ importável a partir de qualquer página do dashboard.
RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import charts  # noqa: E402
from src import analysis, helpers  # noqa: E402


@st.cache_resource
def obter_conector():
    """Conector DuckDB único, reutilizado entre páginas e sessões."""
    return helpers.ConectorBD()


# --------------------------------------------------------------------------
# Tabelas e métricas analíticas
# --------------------------------------------------------------------------


def qualidade_dados():
    """Relatório de nulos e duplicatas (Styler — não cacheável, mas leve)."""
    return analysis.verificar_qualidade_dados(obter_conector())


@st.cache_data(show_spinner="Calculando KPIs gerais...")
def kpis_gerais():
    return analysis.calcular_kpis_gerais(obter_conector())


@st.cache_data(show_spinner="Carregando desempenho mensal...")
def desempenho_mensal():
    return analysis.obter_desempenho_mensal_vendas(obter_conector())


@st.cache_data(show_spinner="Segmentando clientes...")
def segmentacao_clientes():
    return analysis.analisar_segmentacao_clientes(obter_conector())


@st.cache_data(show_spinner="Analisando preferências por gênero...")
def preferencias_genero():
    """Retorna (df_categoria, df_cacau)."""
    return analysis.analisar_preferencias_por_genero(obter_conector())


@st.cache_data(show_spinner="Analisando produtos por cacau...")
def produtos_cacau():
    """Retorna (df_produtos, metricas_intensidade)."""
    return analysis.analisar_produtos_cacau(obter_conector())


@st.cache_data(show_spinner="Avaliando desempenho das lojas...")
def desempenho_lojas():
    return analysis.analisar_desempenho_lojas(obter_conector())


@st.cache_data(show_spinner="Medindo impacto dos descontos...")
def impacto_desconto():
    """Retorna (df_faixas, serie_correlacao)."""
    return analysis.analisar_impacto_desconto(obter_conector())


@st.cache_data(show_spinner="Analisando sazonalidade YoY...")
def sazonalidade_yoy():
    """Retorna (df_pivot, serie_estatisticas)."""
    return analysis.analisar_sazonalidade_yoy(obter_conector())


# --------------------------------------------------------------------------
# Gráficos interativos (Plotly) — figuras serializáveis, cacheadas direto
# --------------------------------------------------------------------------


@st.cache_data(show_spinner="Gerando gráfico de cidades...")
def figura_cidade():
    return charts.grafico_cidade(desempenho_lojas())


@st.cache_data(show_spinner="Gerando gráfico de fidelidade...")
def figura_fidelidade():
    return charts.grafico_fidelidade(obter_conector())


@st.cache_data(show_spinner="Gerando vendas por estação...")
def figura_estacao():
    return charts.grafico_estacao(obter_conector())


@st.cache_data(show_spinner="Gerando consumo por dia da semana...")
def figura_dia_semana():
    return charts.grafico_dia_semana(obter_conector())


@st.cache_data(show_spinner="Gerando tendência diária...")
def figura_tendencia_diaria():
    return charts.grafico_tendencia_diaria(obter_conector())


@st.cache_data(show_spinner="Executando clusterização K-Means...")
def clusterizacao():
    """Roda a clusterização uma única vez e devolve os dois gráficos + dados.

    Retorna (figura_pca, figura_comportamento, distribuicao_clusters).
    """
    df_clusters = charts.executar_clusterizacao(obter_conector())
    figura_pca = charts.grafico_clusters_pca(df_clusters)
    figura_comportamento = charts.grafico_comportamento_clusters(df_clusters)
    distribuicao = df_clusters["nome_cluster"].value_counts()
    return figura_pca, figura_comportamento, distribuicao


@st.cache_data(show_spinner="Analisando receita × lucro...")
def receita_lucro():
    """Retorna (figura, serie_correlacao)."""
    return charts.grafico_relacao_receita_lucro(obter_conector())
