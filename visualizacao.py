import duckdb
import pandas as pd
import matplotlib.pyplot as plt

# 📌 Conexão
conn = duckdb.connect(r"data\chocolate_sales.db")

# 📊 Query base
query = """
SELECT 

    (
        p.product_id || '_' ||
        p.product_name || '_' ||
        p.brand || '_' ||
        p.category || '_' ||
        p.cocoa_percent || '_' ||
        p.weight_g
    ) AS produto,

    CASE 
        WHEN c.month IN (12,1,2) THEN 'Inverno'
        WHEN c.month IN (3,4,5) THEN 'Primavera'
        WHEN c.month IN (6,7,8) THEN 'Verão'
        ELSE 'Outono'
    END AS estacao_do_ano,

    SUM(s.quantity) AS total_vendido

FROM sales s

JOIN products p 
    ON s.product_id = p.product_id

JOIN calendar c 
    ON s.order_date = c.date

GROUP BY produto, estacao_do_ano
"""

df = conn.execute(query).fetchdf()


# ==============================
# 🏆 2. TOP 10 PRODUTOS POR ESTAÇÃO
# ==============================

# 🔥 Criar nome curto
df["produto_curto"] = df["produto"].str.split("_").str[1]

# 🔢 TOP produtos
top_produtos = (
    df.groupby("produto_curto")["total_vendido"]
    .sum()
    .nlargest(10)
    .index
)

df_top = df[df["produto_curto"].isin(top_produtos)]

# 📊 Pivot
pivot = df_top.pivot_table(
    index="estacao_do_ano",
    columns="produto_curto",
    values="total_vendido",
    aggfunc="sum"
)

# 🔄 Ordem correta
ordem_estacoes = ["Inverno", "Primavera", "Verão", "Outono"]
pivot = pivot.reindex(ordem_estacoes)

# 📈 Plot
plt.figure(figsize=(16, 8))

for produto in pivot.columns:
    plt.plot(pivot.index, pivot[produto], marker='o', label=produto)

plt.title("Flutuação de Vendas por Produto ao Longo das Estações")
plt.xlabel("Estação do Ano")
plt.ylabel("Total Vendido")

plt.legend(
    title="Produtos",
    bbox_to_anchor=(1.05, 1),
    loc='upper left'
)

plt.tight_layout()
plt.show()

# MÉDIA DE VENDAS POR DIA DA SEMANA

query_dia = """
SELECT 

    c.day_of_week,

    cu.gender,

    CASE 
        WHEN cu.age < 25 THEN '18-24'
        WHEN cu.age < 35 THEN '25-34'
        WHEN cu.age < 50 THEN '35-49'
        ELSE '50+'
    END AS faixa_idade,

    AVG(s.quantity) AS media_consumo

FROM sales s

JOIN calendar c 
    ON s.order_date = c.date

JOIN customers cu 
    ON s.customer_id = cu.customer_id

GROUP BY 
    c.day_of_week,
    cu.gender,
    faixa_idade
"""

df_dia = conn.execute(query_dia).fetchdf()

mapa_dias = {
    0: "Segunda",
    1: "Terça",
    2: "Quarta",
    3: "Quinta",
    4: "Sexta",
    5: "Sábado",
    6: "Domingo"
}

df_dia["dia_semana"] = df_dia["day_of_week"].map(mapa_dias)

import matplotlib.pyplot as plt

# média total
media_total = (
    df_dia.groupby("dia_semana")["media_consumo"]
    .mean()
    .reset_index()
)

# por gênero
pivot_genero = df_dia.pivot_table(
    index="dia_semana",
    columns="gender",
    values="media_consumo",
    aggfunc="mean"
)

# por faixa etária
pivot_idade = df_dia.pivot_table(
    index="dia_semana",
    columns="faixa_idade",
    values="media_consumo",
    aggfunc="mean"
)

# ordem correta
ordem_dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]

media_total = media_total.set_index("dia_semana").reindex(ordem_dias)
pivot_genero = pivot_genero.reindex(ordem_dias)
pivot_idade = pivot_idade.reindex(ordem_dias)

# 📈 gráfico
plt.figure(figsize=(14, 8))

# média total
plt.plot(media_total.index, media_total["media_consumo"], marker='o', label="Média Total")

# gênero
for col in pivot_genero.columns:
    plt.plot(pivot_genero.index, pivot_genero[col], marker='o', linestyle='--', label=f"Gênero: {col}")

# faixa etária
for col in pivot_idade.columns:
    plt.plot(pivot_idade.index, pivot_idade[col], marker='o', linestyle=':', label=f"Idade: {col}")

plt.title("Consumo Médio de Chocolate por Dia da Semana")
plt.xlabel("Dia da Semana")
plt.ylabel("Média de Consumo")

plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()