import duckdb
import pandas as pd
import matplotlib.pyplot as plt


# 📌 Conexão
conn = duckdb.connect(r"data\chocolate_sales.db")

sales = conn.execute("SELECT * FROM sales").df()
products = conn.execute("SELECT * FROM products").df()
customers = conn.execute("SELECT * FROM customers").df()
calendar = conn.execute("SELECT * FROM calendar").df()


sales['order_date'] = pd.to_datetime(sales['order_date'])
calendar['date'] = pd.to_datetime(calendar['date'])

# --- JOIN DAS TABELAS ---
df = sales.merge(products, on='product_id', how='left') \
          .merge(customers, on='customer_id', how='left') \
          .merge(calendar, left_on='order_date', right_on='date', how='left')

# --- PRODUTO CONCATENADO ---
df['Produto'] = (
    df['product_id'].astype(str) + ' - ' +
    df['product_name'] + ' - ' +
    df['brand'] + ' - ' +
    df['category']
)

# --- GENERO EM PT-BR ---
map_genero = {
    'Male': 'Masculino',
    'Female': 'Feminino'
}
df['Genero_Cliente'] = df['gender'].map(map_genero)

# --- FAIXA ETARIA ---
def faixa_idade(idade):
    if pd.isna(idade):
        return 'Não identificado'
    elif idade <= 24:
        return '18-24'
    elif idade <= 34:
        return '25-34'
    elif idade <= 49:
        return '35-49'
    else:
        return '50+'

df['Idade_Cliente'] = df['age'].apply(faixa_idade)

# --- DIA DA SEMANA EM PT-BR ---
map_dia = {
     0: 'Segunda-feira',
    1: 'Terça-feira',
    2: 'Quarta-feira',
    3: 'Quinta-feira',
    4: 'Sexta-feira',
    5: 'Sábado',
    6: 'Domingo'
}
df['Dia_Semana'] = df['day_of_week'].map(map_dia)

# --- ESTAÇÃO DO ANO ---
def estacao(mes):
    if mes in [12, 1, 2]:
        return 'Verão'
    elif mes in [3, 4, 5]:
        return 'Outono'
    elif mes in [6, 7, 8]:
        return 'Inverno'
    else:
        return 'Primavera'

df['Estacao_Ano'] = df['month'].apply(estacao)

# --- SELEÇÃO FINAL ---
vendas_produto_tempo_clientes = df[[
    'order_id',
    'Produto',
    'Genero_Cliente',
    'Idade_Cliente',
    'Dia_Semana',
    'Estacao_Ano'
]].rename(columns={
    'order_id': 'Ordem_Compra'
})

# --- AMOSTRA ---
print(vendas_produto_tempo_clientes.head(10))

# Analise dos 10 produtos mais vendidos em relação as estações do ano

# -------------------------------
# ANALISE TOP 10 PRODUTOS
# -------------------------------

ordem_estacoes = ['Verão', 'Outono', 'Inverno', 'Primavera']

# Top 10 produtos
top10 = (
    vendas_produto_tempo_clientes
    .groupby('Produto')
    .size()
    .sort_values(ascending=False)
    .head(10)
)

top10_produtos = top10.index

# Filtrar
df_top10 = vendas_produto_tempo_clientes[
    vendas_produto_tempo_clientes['Produto'].isin(top10_produtos)
]

# Agrupar por estação
df_analise = (
    df_top10
    .groupby(['Produto', 'Estacao_Ano'])
    .size()
    .reset_index(name='Quantidade')
)

# Total geral
total_geral = df_top10.shape[0]

# Percentual
df_analise['Percentual'] = df_analise['Quantidade'] / total_geral * 100

# Média por produto
media_produto = (
    df_analise.groupby('Produto')['Quantidade']
    .mean()
    .reset_index(name='Media')
)

df_analise = df_analise.merge(media_produto, on='Produto')

# Ordenar estação
df_analise['Estacao_Ano'] = pd.Categorical(
    df_analise['Estacao_Ano'],
    categories=ordem_estacoes,
    ordered=True
)

df_analise = df_analise.sort_values(['Produto', 'Estacao_Ano'])

# -------------------------------
# GRAFICO
# -------------------------------

plt.figure(figsize=(12,6))

for produto in df_analise['Produto'].unique():
    dados = df_analise[df_analise['Produto'] == produto]
    
    plt.plot(
        dados['Estacao_Ano'],
        dados['Quantidade'],
        marker='o',
        label=produto
    )

plt.title('Top 10 Produtos - Vendas por Estação do Ano')
plt.xlabel('Estação do Ano')
plt.ylabel('Quantidade de Vendas')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()

plt.show()


# LEVANTAMENTO DE CONSUMO DOS CLIENTES FAZENDO A TOTALIZAÇÃO POR DIA DE SEMANA

ordem_dias = [
    'Segunda-feira', 'Terça-feira', 'Quarta-feira',
    'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo'
]

total_dia = (
    vendas_produto_tempo_clientes
    .groupby('Dia_Semana')
    .size()
    .reindex(ordem_dias)
)

genero_dia = (
    vendas_produto_tempo_clientes
    .groupby(['Dia_Semana', 'Genero_Cliente'])
    .size()
    .unstack()
    .reindex(ordem_dias)
)

idade_dia = (
    vendas_produto_tempo_clientes
    .groupby(['Dia_Semana', 'Idade_Cliente'])
    .size()
    .unstack()
    .reindex(ordem_dias)
)

plt.figure(figsize=(12,6))

# Linha total
plt.plot(total_dia.index, total_dia.values, marker='o', label='Total')

# Linhas por gênero
for col in genero_dia.columns:
    plt.plot(genero_dia.index, genero_dia[col], marker='o', linestyle='--', label=col)

# Linhas por idade
for col in idade_dia.columns:
    plt.plot(idade_dia.index, idade_dia[col], marker='o', linestyle=':', label=col)

plt.title('Consumo de Produtos por Dia da Semana')
plt.xlabel('Dia da Semana')
plt.ylabel('Quantidade de Produtos')
plt.xticks(rotation=45)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()

plt.show()

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#     CLUSTERIZAÇÃO COM 4 NÚCLEOS
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

from sklearn.preprocessing import OneHotEncoder
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import pandas as pd

# -------------------------------
# 1. SELEÇÃO DE COLUNAS
# -------------------------------
colunas = ['Genero_Cliente', 'Idade_Cliente', 'Dia_Semana', 'Estacao_Ano']

df_cluster = vendas_produto_tempo_clientes[colunas].copy()

# Tratar nulos (importante)
df_cluster = df_cluster.fillna('Desconhecido')

# -------------------------------
# 2. ONE-HOT ENCODING
# -------------------------------
encoder = OneHotEncoder(sparse_output=False)  # compatível com mais versões

X = encoder.fit_transform(df_cluster)

# -------------------------------
# 3. K-MEANS (4 CLUSTERS)
# -------------------------------
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)

clusters = kmeans.fit_predict(X)

vendas_produto_tempo_clientes['Cluster'] = clusters

# -------------------------------
# 4. PCA (redução para visualização)
# -------------------------------
pca = PCA(n_components=2)

X_pca = pca.fit_transform(X)

# -------------------------------
# 5. GRÁFICO COM LEGENDA
# -------------------------------
plt.figure(figsize=(10,6))

for cluster_id in range(4):
    plt.scatter(
        X_pca[clusters == cluster_id, 0],
        X_pca[clusters == cluster_id, 1],
        label=f'Cluster {cluster_id}'
    )

plt.title('Clusterização de Comportamento de Consumo')
plt.xlabel('Componente Principal 1')
plt.ylabel('Componente Principal 2')
plt.legend()
plt.grid()

plt.show()

# -------------------------------
# 6. INTERPRETAÇÃO DOS CLUSTERS (ESSENCIAL)
# -------------------------------
perfil_clusters = (
    vendas_produto_tempo_clientes
    .groupby('Cluster')[colunas]
    .agg(lambda x: x.mode()[0])
)

print("\nPerfil dos Clusters:")
print(perfil_clusters)

# -------------------------------
# 7. TAMANHO DOS CLUSTERS
# -------------------------------
print("\nDistribuição dos Clusters:")
print(vendas_produto_tempo_clientes['Cluster'].value_counts())





# NOMES AUTOMATICOS

# -------------------------------
# GERAR PERFIL DOS CLUSTERS
# -------------------------------
colunas = ['Genero_Cliente', 'Idade_Cliente', 'Dia_Semana', 'Estacao_Ano']

perfil_clusters = (
    vendas_produto_tempo_clientes
    .groupby('Cluster')[colunas]
    .agg(lambda x: x.mode()[0])
)

# -------------------------------
# FUNÇÃO PARA CRIAR NOME AUTOMÁTICO
# -------------------------------
def gerar_nome_cluster(row):
    return f"{row['Genero_Cliente']} | {row['Idade_Cliente']} | {row['Dia_Semana']} | {row['Estacao_Ano']}"

# Criar nomes
nomes_clusters = perfil_clusters.apply(gerar_nome_cluster, axis=1)

# Converter para dicionário
mapa_clusters = nomes_clusters.to_dict()

# Aplicar no dataframe
vendas_produto_tempo_clientes['Cluster_Nome'] = (
    vendas_produto_tempo_clientes['Cluster'].map(mapa_clusters)
)

# Mostrar resultado
print("\nNomes automáticos dos clusters:")
print(mapa_clusters)


# GRAFICOS

tabela = pd.crosstab(
    vendas_produto_tempo_clientes['Dia_Semana'],
    vendas_produto_tempo_clientes['Cluster_Nome']
)

tabela.plot(kind='line', marker='o')

plt.title('Comportamento por Perfil de Cliente')
plt.xlabel('Dia da Semana')
plt.ylabel('Quantidade')
plt.xticks(rotation=45)

plt.legend(title='Perfil')

plt.show()





