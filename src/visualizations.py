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