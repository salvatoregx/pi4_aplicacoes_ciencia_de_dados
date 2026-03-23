import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output"
)


def _salvar_figura(nome_arquivo):
    """Salva a figura atual na pasta de saída."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    plt.savefig(
        os.path.join(OUTPUT_DIR, nome_arquivo),
        dpi=150,
        bbox_inches="tight",
    )


def visualizar_desempenho_por_cidade(desempenho_por_cidade):
    """
    Gráfico de barras comparando receita, lucro e volume de vendas por cidade.
    Recebe o DataFrame retornado por analysis.analisar_desempenho_lojas.
    """
    metricas = [
        ("receita_total", "Receita Total por Cidade", "Receita Total"),
        ("lucro_total", "Lucro Total por Cidade", "Lucro Total"),
        ("itens_vendidos", "Itens Vendidos por Cidade", "Itens Vendidos"),
    ]

    dados_cidade = (
        desempenho_por_cidade.groupby("city")[
            ["receita_total", "lucro_total", "itens_vendidos"]
        ]
        .sum()
        .sort_values("receita_total", ascending=False)
        .reset_index()
    )

    cidades = dados_cidade["city"]
    cores = cm.viridis(np.linspace(0.2, 0.9, len(cidades)))

    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    fig.suptitle("Desempenho de Vendas por Cidade", fontsize=16)

    for ax, (coluna, titulo, rotulo_y) in zip(axes, metricas):
        ax.bar(cidades, dados_cidade[coluna], color=cores)
        ax.set_title(titulo)
        ax.set_xlabel("Cidade")
        ax.set_ylabel(rotulo_y)
        ax.ticklabel_format(style="plain", axis="y")
        ax.tick_params(axis="x", rotation=45)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    _salvar_figura("desempenho_por_cidade.png")
    plt.show()


def visualizar_fidelidade(conector):
    """
    Compara ticket médio e frequência de compras entre membros do
    programa de fidelidade e não-membros.
    """
    consulta = """
        SELECT
            c.loyalty_member,
            s.customer_id,
            s.order_id,
            s.revenue
        FROM sales s
        JOIN customers c ON s.customer_id = c.customer_id
    """
    df = conector.executar_consulta_personalizada(consulta)
    df["tipo_cliente"] = df["loyalty_member"].map(
        {1: "Membro Fidelidade", 0: "Não-Membro"}
    )

    ticket_medio = (
        df.groupby("tipo_cliente")["revenue"]
        .mean()
        .reset_index()
        .rename(columns={"revenue": "ticket_medio"})
    )

    frequencia = (
        df.groupby(["tipo_cliente", "customer_id"])["order_id"]
        .count()
        .reset_index()
        .rename(columns={"order_id": "num_compras"})
        .groupby("tipo_cliente")["num_compras"]
        .mean()
        .reset_index()
        .rename(columns={"num_compras": "frequencia_media"})
    )

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Membros Fidelidade vs Não-Membros", fontsize=16, fontweight="bold")
    cores = ["#2ecc71", "#e74c3c"]

    barras1 = ax1.bar(
        ticket_medio["tipo_cliente"],
        ticket_medio["ticket_medio"],
        color=cores,
        width=0.5,
    )
    ax1.set_title("Ticket Médio por Pedido (R$)", fontsize=13, fontweight="bold")
    ax1.set_ylabel("Receita Média (R$)")
    ax1.set_ylim(0, ticket_medio["ticket_medio"].max() * 1.3)
    for barra in barras1:
        altura = barra.get_height()
        ax1.text(
            barra.get_x() + barra.get_width() / 2,
            altura + 0.2,
            f"R$ {altura:.2f}",
            ha="center",
            fontweight="bold",
        )

    barras2 = ax2.bar(
        frequencia["tipo_cliente"],
        frequencia["frequencia_media"],
        color=cores,
        width=0.5,
    )
    ax2.set_title(
        "Frequência Média de Compras por Cliente", fontsize=13, fontweight="bold"
    )
    ax2.set_ylabel("Nº Médio de Pedidos")
    ax2.set_ylim(0, frequencia["frequencia_media"].max() * 1.3)
    for barra in barras2:
        altura = barra.get_height()
        ax2.text(
            barra.get_x() + barra.get_width() / 2,
            altura + 0.2,
            f"{altura:.1f} pedidos",
            ha="center",
            fontweight="bold",
        )

    plt.tight_layout()
    _salvar_figura("visualizacao_fidelidade.png")
    plt.show()


def visualizar_vendas_por_estacao(conector):
    """
    Gráfico de linhas mostrando a flutuação de vendas dos 10 produtos
    mais vendidos ao longo das estações do ano.
    """
    consulta = """
        SELECT
            p.product_name AS produto,
            CASE
                WHEN c.month IN (12, 1, 2) THEN 'Inverno'
                WHEN c.month IN (3, 4, 5)  THEN 'Primavera'
                WHEN c.month IN (6, 7, 8)  THEN 'Verão'
                ELSE 'Outono'
            END AS estacao,
            SUM(s.quantity) AS total_vendido
        FROM sales s
        JOIN products p  ON s.product_id = p.product_id
        JOIN calendar c  ON s.order_date = c.date
        GROUP BY produto, estacao
    """
    df = conector.executar_consulta_personalizada(consulta)

    # Seleciona os 10 produtos com maior volume total
    top_produtos = df.groupby("produto")["total_vendido"].sum().nlargest(10).index
    df_top = df[df["produto"].isin(top_produtos)]

    # Pivoteia por estação
    tabela_pivot = df_top.pivot_table(
        index="estacao",
        columns="produto",
        values="total_vendido",
        aggfunc="sum",
    )
    ordem_estacoes = ["Inverno", "Primavera", "Verão", "Outono"]
    tabela_pivot = tabela_pivot.reindex(ordem_estacoes)

    plt.figure(figsize=(16, 8))
    for produto in tabela_pivot.columns:
        plt.plot(tabela_pivot.index, tabela_pivot[produto], marker="o", label=produto)

    plt.title("Flutuação de Vendas por Produto ao Longo das Estações")
    plt.xlabel("Estação do Ano")
    plt.ylabel("Total Vendido")
    plt.legend(title="Produtos", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    _salvar_figura("vendas_por_estacao.png")
    plt.show()


def visualizar_consumo_por_dia_semana(conector):
    """
    Gráfico de linhas mostrando o consumo médio de chocolate por dia
    da semana, segmentado por gênero e faixa etária.
    """
    consulta = """
        SELECT
            c.day_of_week,
            cu.gender         AS genero,
            CASE
                WHEN cu.age < 25 THEN '18-24'
                WHEN cu.age < 35 THEN '25-34'
                WHEN cu.age < 50 THEN '35-49'
                ELSE '50+'
            END AS faixa_idade,
            AVG(s.quantity) AS media_consumo
        FROM sales s
        JOIN calendar  c  ON s.order_date  = c.date
        JOIN customers cu ON s.customer_id = cu.customer_id
        GROUP BY c.day_of_week, genero, faixa_idade
    """
    df = conector.executar_consulta_personalizada(consulta)

    mapa_dias = {
        0: "Segunda",
        1: "Terça",
        2: "Quarta",
        3: "Quinta",
        4: "Sexta",
        5: "Sábado",
        6: "Domingo",
    }
    df["dia_semana"] = df["day_of_week"].map(mapa_dias)
    ordem_dias = list(mapa_dias.values())

    # Média total por dia
    media_total = df.groupby("dia_semana")["media_consumo"].mean().reindex(ordem_dias)

    # Por gênero
    pivot_genero = df.pivot_table(
        index="dia_semana", columns="genero", values="media_consumo", aggfunc="mean"
    ).reindex(ordem_dias)

    # Por faixa etária
    pivot_idade = df.pivot_table(
        index="dia_semana",
        columns="faixa_idade",
        values="media_consumo",
        aggfunc="mean",
    ).reindex(ordem_dias)

    plt.figure(figsize=(14, 8))
    plt.plot(media_total.index, media_total.values, marker="o", label="Média Total")

    for col in pivot_genero.columns:
        plt.plot(
            pivot_genero.index,
            pivot_genero[col],
            marker="o",
            linestyle="--",
            label=f"Gênero: {col}",
        )

    for col in pivot_idade.columns:
        plt.plot(
            pivot_idade.index,
            pivot_idade[col],
            marker="o",
            linestyle=":",
            label=f"Idade: {col}",
        )

    plt.title("Consumo Médio de Chocolate por Dia da Semana")
    plt.xlabel("Dia da Semana")
    plt.ylabel("Média de Consumo")
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.xticks(rotation=45)
    plt.tight_layout()
    _salvar_figura("consumo_por_dia_semana.png")
    plt.show()


def visualizar_clusterizacao(conector):
    """
    Clusterização K-Means (4 clusters) sobre perfil demográfico e temporal
    dos clientes, com visualização PCA. Retorna DataFrame com colunas
    'cluster' e 'nome_cluster'.
    """
    from sklearn.preprocessing import OneHotEncoder
    from sklearn.cluster import KMeans
    from sklearn.decomposition import PCA

    # Carrega e prepara os dados
    consulta = """
        SELECT
            s.order_id,
            cu.gender          AS genero,
            CASE
                WHEN cu.age < 25 THEN '18-24'
                WHEN cu.age < 35 THEN '25-34'
                WHEN cu.age < 50 THEN '35-49'
                ELSE '50+'
            END AS faixa_idade,
            CASE
                WHEN c.day_of_week = 0 THEN 'Segunda-feira'
                WHEN c.day_of_week = 1 THEN 'Terça-feira'
                WHEN c.day_of_week = 2 THEN 'Quarta-feira'
                WHEN c.day_of_week = 3 THEN 'Quinta-feira'
                WHEN c.day_of_week = 4 THEN 'Sexta-feira'
                WHEN c.day_of_week = 5 THEN 'Sábado'
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
    df_vendas = conector.executar_consulta_personalizada(consulta)

    colunas_cluster = ["genero", "faixa_idade", "dia_semana", "estacao"]
    df_cluster = df_vendas[colunas_cluster].fillna("Desconhecido")

    # Encoding e clusterização
    codificador = OneHotEncoder(sparse_output=False)
    X = codificador.fit_transform(df_cluster)

    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    rotulos = kmeans.fit_predict(X)
    df_vendas["cluster"] = rotulos

    # Nomes automáticos baseados no perfil predominante
    perfil = df_vendas.groupby("cluster")[colunas_cluster].agg(lambda x: x.mode()[0])
    mapa_nomes = perfil.apply(
        lambda r: (
            f"{r['genero']} | {r['faixa_idade']} | {r['dia_semana']} | {r['estacao']}"
        ),
        axis=1,
    ).to_dict()
    df_vendas["nome_cluster"] = df_vendas["cluster"].map(mapa_nomes)

    # --- Gráfico PCA ---
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X)

    plt.figure(figsize=(10, 6))
    for id_cluster in range(4):
        mascara = rotulos == id_cluster
        plt.scatter(
            X_pca[mascara, 0],
            X_pca[mascara, 1],
            label=f"Cluster {id_cluster}",
            alpha=0.6,
        )

    plt.title("Clusterização de Comportamento de Consumo (PCA)")
    plt.xlabel("Componente Principal 1")
    plt.ylabel("Componente Principal 2")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    _salvar_figura("clusterizacao_pca.png")
    plt.show()

    # --- Perfil e distribuição (impresso no notebook) ---
    print("\nPerfil dos Clusters:")
    print(perfil)
    print("\nDistribuição dos Clusters:")
    print(df_vendas["cluster"].value_counts().sort_index())

    return df_vendas


def visualizar_comportamento_clusters(df_vendas):
    """
    Volume de compras por dia da semana para cada perfil de cluster.
    Recebe o DataFrame retornado por visualizar_clusterizacao.
    """
    tabela = pd.crosstab(df_vendas["dia_semana"], df_vendas["nome_cluster"])

    ordem_dias = [
        "Segunda-feira",
        "Terça-feira",
        "Quarta-feira",
        "Quinta-feira",
        "Sexta-feira",
        "Sábado",
        "Domingo",
    ]
    tabela = tabela.reindex(ordem_dias)

    plt.figure(figsize=(12, 6))
    for coluna in tabela.columns:
        plt.plot(tabela.index, tabela[coluna], marker="o", label=coluna)

    plt.title("Comportamento por Perfil de Cliente")
    plt.xlabel("Dia da Semana")
    plt.ylabel("Quantidade")
    plt.xticks(rotation=45)
    plt.legend(title="Perfil", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    _salvar_figura("comportamento_clusters.png")
    plt.show()


def visualizar_tendencia_diaria(conector):
    """Gráfico de tendência diária de receita e volume. """
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

    df["media_movel_receita"] = df["receita_total"].rolling(window=14, min_periods=1).mean()
    df["media_movel_itens"] = df["itens_vendidos"].rolling(window=14, min_periods=1).mean()

    fig, ax1 = plt.subplots(figsize=(14, 6))
    ax1.plot(df.index, df["receita_total"], color="#3498db", alpha=0.4, label="Receita diária")
    ax1.plot(df.index, df["media_movel_receita"], color="#1f77b4", linewidth=2, label="Média móvel 14 dias (receita)")
    ax1.set_ylabel("Receita (R$)", color="#1f77b4")
    ax1.ticklabel_format(style="plain", axis="y")

    ax2 = ax1.twinx()
    ax2.plot(df.index, df["itens_vendidos"], color="#e67e22", alpha=0.4, label="Itens vendidos diários")
    ax2.plot(df.index, df["media_movel_itens"], color="#d35400", linewidth=2, label="Média móvel 14 dias (itens)")
    ax2.set_ylabel("Itens vendidos", color="#d35400")

    fig.suptitle("Tendência Diária de Receita e Volume de Vendas", fontsize=16, fontweight="bold")
    ax1.set_xlabel("Data")

    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc="upper left", fontsize=9)

    plt.xticks(rotation=45)
    plt.tight_layout()
    _salvar_figura("tendencia_diaria.png")
    plt.show()
