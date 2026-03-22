import matplotlib.pyplot as plt
import seaborn as sns

def visualizar_desempenho_por_cidade(desempenho_por_cidade):

    # Plotting performance by city
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    fig.suptitle('Desempenho de Vendas por Cidade', fontsize=16)

    sns.barplot(x='city', y='receita_total', data=desempenho_por_cidade, ax=axes[0], palette='viridis', hue='city', legend=False)
    axes[0].set_title('Receita Total por Cidade')
    axes[0].set_xlabel('Cidade')
    axes[0].set_ylabel('Receita Total')
    axes[0].ticklabel_format(style='plain', axis='y')

    sns.barplot(x='city', y='lucro_total', data=desempenho_por_cidade, ax=axes[1], palette='viridis', hue='city', legend=False)
    axes[1].set_title('Lucro Total por Cidade')
    axes[1].set_xlabel('Cidade')
    axes[1].set_ylabel('Lucro Total')
    axes[1].ticklabel_format(style='plain', axis='y')

    sns.barplot(x='city', y='itens_vendidos', data=desempenho_por_cidade, ax=axes[2], palette='viridis', hue='city', legend=False)
    axes[2].set_title('Itens Vendidos por Cidade')
    axes[2].set_xlabel('Cidade')
    axes[2].set_ylabel('Itens Vendidos')
    axes[2].ticklabel_format(style='plain', axis='y')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

def visualizar_fidelidade(conector):
    import pandas as pd

    query = """
        SELECT
            c.loyalty_member,
            s.customer_id,
            s.order_id,
            s.revenue
        FROM sales s
        JOIN customers c ON s.customer_id = c.customer_id
    """
    df = conector.executar_consulta_personalizada(query)
    df["tipo_cliente"] = df["loyalty_member"].map({1: "Membro Fidelidade", 0: "Não-Membro"})

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

    bars1 = ax1.bar(ticket_medio["tipo_cliente"], ticket_medio["ticket_medio"], color=cores, width=0.5)
    ax1.set_title("Ticket Médio por Pedido (R$)", fontsize=13, fontweight="bold")
    ax1.set_ylabel("Receita Média (R$)")
    ax1.set_ylim(0, ticket_medio["ticket_medio"].max() * 1.3)
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, height + 0.2, f"R$ {height:.2f}", ha="center", fontweight="bold")

    bars2 = ax2.bar(frequencia["tipo_cliente"], frequencia["frequencia_media"], color=cores, width=0.5)
    ax2.set_title("Frequência Média de Compras por Cliente", fontsize=13, fontweight="bold")
    ax2.set_ylabel("Nº Médio de Pedidos")
    ax2.set_ylim(0, frequencia["frequencia_media"].max() * 1.3)
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, height + 0.2, f"{height:.1f} pedidos", ha="center", fontweight="bold")

    plt.tight_layout()
    plt.savefig("visualizacao_fidelidade.png", dpi=150, bbox_inches="tight")
    plt.show()
