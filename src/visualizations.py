import duckdb
import pandas as pd
import matplotlib.pyplot as plt

# Classe de conexão
class ConectorBD:
    def __init__(self, caminho_banco):
        self.con = duckdb.connect(caminho_banco)

    def obter_tabela_bruta(self, nome_tabela):
        query = f"SELECT * FROM {nome_tabela}"
        return self.con.execute(query).df()


# Função de análise
def analisar_relacao_receita_lucro(conector):

    # 1. Buscar dados
    df = conector.obter_tabela_bruta('sales')

    # 2. Limpeza
    df = df[['revenue', 'profit']].dropna()

    # 3. Correlação
    correlacao = df['revenue'].corr(df['profit'])
    print(f"Correlação entre Receita e Lucro: {correlacao:.4f}")

    # 4. Gráfico
    plt.figure(figsize=(8, 5))

    plt.scatter(
        df['revenue'],
        df['profit'],
        alpha=0.6
    )

    # UNIDADE ADICIONADA
    plt.title("Relação entre Receita e Lucro")
    plt.xlabel("Receita (R$)")
    plt.ylabel("Lucro (R$)")

    # Linha de tendência
    z = df['revenue']
    p = df['profit']

    m = z.cov(p) / z.var()
    b = p.mean() - (m * z.mean())

    plt.plot(z, m*z + b)

    plt.grid(True)
    plt.show()

    # 5. Resultado
    return pd.Series({
        'Correlação Receita x Lucro': f"{correlacao:.4f}",
        'Tipo de Relação': (
            'Forte positiva' if correlacao > 0.7 else
            'Moderada' if correlacao > 0.4 else
            'Fraca'
        )
    }, name="Análise Receita vs Lucro")


# EXECUÇÃO
if __name__ == "__main__":

    # cria conexão
    conector = ConectorBD("../data/chocolate_sales.db")

    # roda análise
    resultado = analisar_relacao_receita_lucro(conector)

    # imprime resultado
    print(resultado)