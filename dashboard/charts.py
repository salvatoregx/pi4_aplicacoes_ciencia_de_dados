"""Visualizações interativas (Plotly) para o dashboard.

Equivalentes da 2.ª etapa às figuras Matplotlib de ``src/visualizations.py``.
O módulo ``src/`` é mantido intacto (entrega da 1.ª etapa); aqui as mesmas
análises são reconstruídas com Plotly para permitir interatividade (zoom,
hover, alternância de séries) e cache nativo no Streamlit.
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

ORDEM_DIAS = [
    "Segunda-feira",
    "Terça-feira",
    "Quarta-feira",
    "Quinta-feira",
    "Sexta-feira",
    "Sábado",
    "Domingo",
]
ORDEM_ESTACOES = ["Verão", "Outono", "Inverno", "Primavera"]

# Limite de pontos plotados em dispersões (a amostragem mantém o navegador
# fluido sem alterar correlações, calculadas sempre sobre a base completa).
TAMANHO_AMOSTRA = 8000


def _layout(fig, titulo, eixo_x=None, eixo_y=None):
    """Aplica tema e títulos padronizados a uma figura."""
    fig.update_layout(
        title=titulo,
        template="plotly_white",
        margin=dict(t=70, l=60, r=40, b=60),
        legend=dict(orientation="h", yanchor="bottom", y=-0.3),
    )
    if eixo_x:
        fig.update_xaxes(title_text=eixo_x)
    if eixo_y:
        fig.update_yaxes(title_text=eixo_y)
    return fig


# --------------------------------------------------------------------------
# 1. Desempenho por cidade
# --------------------------------------------------------------------------
def grafico_cidade(lojas):
    """Barras de receita, lucro e volume por cidade (recebe o DataFrame de lojas)."""
    dados = (
        lojas.groupby("city")[["receita_total", "lucro_total", "itens_vendidos"]]
        .sum()
        .sort_values("receita_total", ascending=False)
        .reset_index()
    )

    fig = make_subplots(
        rows=1,
        cols=3,
        subplot_titles=(
            "Receita Total por Cidade",
            "Lucro Total por Cidade",
            "Itens Vendidos por Cidade",
        ),
    )
    colunas = [
        ("receita_total", "#4c78a8"),
        ("lucro_total", "#54a24b"),
        ("itens_vendidos", "#e45756"),
    ]
    for indice, (coluna, cor) in enumerate(colunas, start=1):
        fig.add_trace(
            go.Bar(
                x=dados["city"],
                y=dados[coluna],
                marker_color=cor,
                showlegend=False,
                hovertemplate="%{x}<br>%{y:,.0f}<extra></extra>",
            ),
            row=1,
            col=indice,
        )
    fig.update_layout(
        title="Desempenho de Vendas por Cidade",
        template="plotly_white",
        height=480,
        margin=dict(t=90, b=80),
    )
    fig.update_xaxes(tickangle=-45)
    return fig


# --------------------------------------------------------------------------
# 2. Fidelidade
# --------------------------------------------------------------------------
def grafico_fidelidade(conector):
    """Ticket médio e frequência de compras: membros vs não-membros."""
    consulta = """
        SELECT c.loyalty_member, s.customer_id, s.order_id, s.revenue
        FROM sales s
        JOIN customers c ON s.customer_id = c.customer_id
    """
    df = conector.executar_consulta_personalizada(consulta)
    df["tipo_cliente"] = df["loyalty_member"].map(
        {1: "Membro Fidelidade", 0: "Não-Membro"}
    )

    ticket_medio = df.groupby("tipo_cliente")["revenue"].mean()
    frequencia = (
        df.groupby(["tipo_cliente", "customer_id"])["order_id"]
        .count()
        .groupby("tipo_cliente")
        .mean()
    )

    cores = {"Membro Fidelidade": "#2ecc71", "Não-Membro": "#e74c3c"}
    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=(
            "Ticket Médio por Pedido (R$)",
            "Frequência Média de Compras por Cliente",
        ),
    )
    fig.add_trace(
        go.Bar(
            x=ticket_medio.index,
            y=ticket_medio.values,
            marker_color=[cores[t] for t in ticket_medio.index],
            text=[f"R$ {v:.2f}" for v in ticket_medio.values],
            textposition="outside",
            showlegend=False,
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Bar(
            x=frequencia.index,
            y=frequencia.values,
            marker_color=[cores[t] for t in frequencia.index],
            text=[f"{v:.1f} pedidos" for v in frequencia.values],
            textposition="outside",
            showlegend=False,
        ),
        row=1,
        col=2,
    )
    fig.update_layout(
        title="Membros Fidelidade vs Não-Membros",
        template="plotly_white",
        height=460,
        margin=dict(t=90),
    )
    return fig


# --------------------------------------------------------------------------
# 3. Vendas por estação do ano
# --------------------------------------------------------------------------
def grafico_estacao(conector):
    """Linhas: vendas dos 10 produtos mais vendidos por estação do ano."""
    consulta = """
        SELECT
            s.order_id,
            (p.product_id || ' - ' || p.product_name || ' - '
             || p.brand || ' - ' || p.category) AS produto,
            CASE
                WHEN c.month IN (12, 1, 2) THEN 'Verão'
                WHEN c.month IN (3, 4, 5)  THEN 'Outono'
                WHEN c.month IN (6, 7, 8)  THEN 'Inverno'
                ELSE 'Primavera'
            END AS estacao
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        JOIN calendar c ON s.order_date = c.date
    """
    df = conector.executar_consulta_personalizada(consulta)

    top10 = df.groupby("produto").size().sort_values(ascending=False).head(10).index
    df_top10 = df[df["produto"].isin(top10)]
    df_analise = (
        df_top10.groupby(["produto", "estacao"]).size().reset_index(name="quantidade")
    )

    fig = px.line(
        df_analise,
        x="estacao",
        y="quantidade",
        color="produto",
        markers=True,
        category_orders={"estacao": ORDEM_ESTACOES},
    )
    fig.update_layout(height=560, legend=dict(orientation="v", x=1.02, y=1))
    return _layout(
        fig,
        "Top 10 Produtos — Vendas por Estação do Ano",
        "Estação do Ano",
        "Quantidade de Vendas",
    )


# --------------------------------------------------------------------------
# 4. Consumo por dia da semana
# --------------------------------------------------------------------------
def grafico_dia_semana(conector):
    """Linhas: consumo por dia da semana, total e segmentado por gênero/idade."""
    consulta = """
        SELECT
            s.order_id,
            CASE cu.gender
                WHEN 'Male'   THEN 'Masculino'
                WHEN 'Female' THEN 'Feminino'
            END AS genero,
            CASE
                WHEN cu.age IS NULL THEN 'Não identificado'
                WHEN cu.age <= 24   THEN '18-24'
                WHEN cu.age <= 34   THEN '25-34'
                WHEN cu.age <= 49   THEN '35-49'
                ELSE '50+'
            END AS faixa_idade,
            CASE c.day_of_week
                WHEN 0 THEN 'Segunda-feira'
                WHEN 1 THEN 'Terça-feira'
                WHEN 2 THEN 'Quarta-feira'
                WHEN 3 THEN 'Quinta-feira'
                WHEN 4 THEN 'Sexta-feira'
                WHEN 5 THEN 'Sábado'
                ELSE 'Domingo'
            END AS dia_semana
        FROM sales s
        JOIN calendar  c  ON s.order_date  = c.date
        JOIN customers cu ON s.customer_id = cu.customer_id
    """
    df = conector.executar_consulta_personalizada(consulta)

    total_dia = df.groupby("dia_semana").size().reindex(ORDEM_DIAS)
    genero_dia = (
        df.groupby(["dia_semana", "genero"]).size().unstack().reindex(ORDEM_DIAS)
    )
    idade_dia = (
        df.groupby(["dia_semana", "faixa_idade"]).size().unstack().reindex(ORDEM_DIAS)
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=ORDEM_DIAS,
            y=total_dia.values,
            mode="lines+markers",
            name="Total",
            line=dict(width=3),
        )
    )
    for coluna in genero_dia.columns:
        fig.add_trace(
            go.Scatter(
                x=ORDEM_DIAS,
                y=genero_dia[coluna].values,
                mode="lines+markers",
                name=coluna,
                line=dict(dash="dash"),
            )
        )
    for coluna in idade_dia.columns:
        fig.add_trace(
            go.Scatter(
                x=ORDEM_DIAS,
                y=idade_dia[coluna].values,
                mode="lines+markers",
                name=coluna,
                line=dict(dash="dot"),
            )
        )
    fig.update_layout(height=520)
    return _layout(
        fig,
        "Consumo de Produtos por Dia da Semana",
        "Dia da Semana",
        "Quantidade de Produtos",
    )


# --------------------------------------------------------------------------
# 5. Clusterização (K-Means) — cálculo + gráficos
# --------------------------------------------------------------------------
def executar_clusterizacao(conector):
    """Roda K-Means (4 clusters) sobre o perfil demográfico/temporal.

    Devolve o DataFrame de vendas com as colunas ``cluster``, ``nome_cluster``
    e as coordenadas PCA (``pca_x``, ``pca_y``).
    """
    from sklearn.cluster import KMeans
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import OneHotEncoder

    consulta = """
        SELECT
            s.order_id,
            CASE cu.gender
                WHEN 'Male'   THEN 'Masculino'
                WHEN 'Female' THEN 'Feminino'
            END AS genero,
            CASE
                WHEN cu.age IS NULL THEN 'Não identificado'
                WHEN cu.age <= 24   THEN '18-24'
                WHEN cu.age <= 34   THEN '25-34'
                WHEN cu.age <= 49   THEN '35-49'
                ELSE '50+'
            END AS faixa_idade,
            CASE c.day_of_week
                WHEN 0 THEN 'Segunda-feira'
                WHEN 1 THEN 'Terça-feira'
                WHEN 2 THEN 'Quarta-feira'
                WHEN 3 THEN 'Quinta-feira'
                WHEN 4 THEN 'Sexta-feira'
                WHEN 5 THEN 'Sábado'
                ELSE 'Domingo'
            END AS dia_semana,
            CASE
                WHEN c.month IN (12, 1, 2) THEN 'Verão'
                WHEN c.month IN (3, 4, 5)  THEN 'Outono'
                WHEN c.month IN (6, 7, 8)  THEN 'Inverno'
                ELSE 'Primavera'
            END AS estacao
        FROM sales s
        JOIN customers cu ON s.customer_id = cu.customer_id
        JOIN calendar  c  ON s.order_date  = c.date
    """
    df = conector.executar_consulta_personalizada(consulta)

    colunas = ["genero", "faixa_idade", "dia_semana", "estacao"]
    df_cluster = df[colunas].fillna("Desconhecido")

    codificador = OneHotEncoder(sparse_output=False)
    X = codificador.fit_transform(df_cluster)

    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    df["cluster"] = kmeans.fit_predict(X)

    perfil = df.groupby("cluster")[colunas].agg(lambda x: x.mode()[0])
    mapa_nomes = perfil.apply(
        lambda r: f"{r['genero']} | {r['faixa_idade']} | "
        f"{r['dia_semana']} | {r['estacao']}",
        axis=1,
    ).to_dict()
    df["nome_cluster"] = df["cluster"].map(mapa_nomes)

    coordenadas = PCA(n_components=2).fit_transform(X)
    df["pca_x"] = coordenadas[:, 0]
    df["pca_y"] = coordenadas[:, 1]
    return df


def grafico_clusters_pca(df_clusters):
    """Dispersão PCA dos clusters (amostrada para manter o navegador fluido)."""
    amostra = df_clusters.sample(
        n=min(TAMANHO_AMOSTRA, len(df_clusters)), random_state=42
    ).sort_values("cluster")

    fig = px.scatter(
        amostra,
        x="pca_x",
        y="pca_y",
        color="nome_cluster",
        opacity=0.6,
    )
    fig.update_layout(height=520)
    return _layout(
        fig,
        "Clusterização de Comportamento de Consumo (PCA)",
        "Componente Principal 1",
        "Componente Principal 2",
    )


def grafico_comportamento_clusters(df_clusters):
    """Linhas: volume de compras de cada cluster por dia da semana."""
    tabela = pd.crosstab(
        df_clusters["dia_semana"], df_clusters["nome_cluster"]
    ).reindex(ORDEM_DIAS)

    fig = go.Figure()
    for coluna in tabela.columns:
        fig.add_trace(
            go.Scatter(
                x=ORDEM_DIAS,
                y=tabela[coluna].values,
                mode="lines+markers",
                name=coluna,
            )
        )
    fig.update_layout(height=480)
    return _layout(
        fig,
        "Comportamento por Perfil de Cliente",
        "Dia da Semana",
        "Quantidade",
    )


# --------------------------------------------------------------------------
# 6. Tendência diária de receita e volume
# --------------------------------------------------------------------------
def grafico_tendencia_diaria(conector):
    """Linha de receita e volume diários com médias móveis de 14 dias."""
    consulta = """
        SELECT
            c.date AS data,
            SUM(s.revenue) AS receita_total,
            SUM(s.quantity) AS itens_vendidos
        FROM sales s
        JOIN calendar c ON s.order_date = c.date
        GROUP BY c.date
        ORDER BY c.date
    """
    df = conector.executar_consulta_personalizada(consulta)
    df["data"] = pd.to_datetime(df["data"])
    df = df.set_index("data").asfreq("D").fillna(0)
    df["media_movel_receita"] = (
        df["receita_total"].rolling(window=14, min_periods=1).mean()
    )
    df["media_movel_itens"] = (
        df["itens_vendidos"].rolling(window=14, min_periods=1).mean()
    )

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["receita_total"],
            name="Receita diária",
            line=dict(color="#3498db"),
            opacity=0.4,
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["media_movel_receita"],
            name="Média móvel 14d (receita)",
            line=dict(color="#1f77b4", width=3),
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["itens_vendidos"],
            name="Itens vendidos diários",
            line=dict(color="#e67e22"),
            opacity=0.4,
        ),
        secondary_y=True,
    )
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["media_movel_itens"],
            name="Média móvel 14d (itens)",
            line=dict(color="#d35400", width=3),
        ),
        secondary_y=True,
    )
    fig.update_yaxes(title_text="Receita (R$)", secondary_y=False)
    fig.update_yaxes(title_text="Itens vendidos", secondary_y=True)
    fig.update_layout(height=500)
    return _layout(
        fig, "Tendência Diária de Receita e Volume de Vendas", "Data"
    )


# --------------------------------------------------------------------------
# 7. Relação entre receita e lucro
# --------------------------------------------------------------------------
def grafico_relacao_receita_lucro(conector):
    """Dispersão receita × lucro com linha de tendência. Retorna (fig, série)."""
    df = conector.obter_tabela_bruta("sales")[["revenue", "profit"]].dropna()
    correlacao = df["revenue"].corr(df["profit"])

    # Regressão linear simples sobre a base completa.
    m = df["revenue"].cov(df["profit"]) / df["revenue"].var()
    b = df["profit"].mean() - m * df["revenue"].mean()

    amostra = df.sample(n=min(TAMANHO_AMOSTRA, len(df)), random_state=42)
    extremos = np.array([df["revenue"].min(), df["revenue"].max()])

    fig = go.Figure()
    fig.add_trace(
        go.Scattergl(
            x=amostra["revenue"],
            y=amostra["profit"],
            mode="markers",
            name="Vendas (amostra)",
            marker=dict(opacity=0.5, color="#4c78a8"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=extremos,
            y=m * extremos + b,
            mode="lines",
            name="Tendência",
            line=dict(color="red", width=2),
        )
    )
    fig.update_layout(height=500)
    _layout(fig, "Relação entre Receita e Lucro", "Receita (R$)", "Lucro (R$)")

    serie = pd.Series(
        {
            "Correlação Receita x Lucro": f"{correlacao:.4f}",
            "Tipo de Relação": (
                "Forte positiva"
                if correlacao > 0.7
                else "Moderada"
                if correlacao > 0.4
                else "Fraca"
            ),
        },
        name="Análise Receita vs Lucro",
    )
    return fig, serie
