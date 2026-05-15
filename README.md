# PI4 — Ciência de Dados Aplicada a Situações de Mercado

Projeto Integrador do 4.º semestre do curso Tecnólogo em Banco de Dados (SENAC EAD).

## Objetivo

Construir uma prova de conceito de modelo de inteligência de negócios que realiza análise exploratória de dados (EDA) com visualizações orientadas à tomada de decisão.

## Dataset

[Chocolate Sales](https://www.kaggle.com/datasets/ssssws/chocolate-sales-dataset-2023-2024) — dados de vendas de chocolates com informações de produtos, clientes, lojas e calendário. O banco DuckDB (`data/chocolate_sales.db`) contém cinco tabelas: `sales`, `products`, `customers`, `stores` e `calendar`.

## Escopo da análise

| Pergunta de negócio | Análise | Visualização |
|---|---|---|
| Os dados são confiáveis para análise? | Qualidade (nulos, duplicatas) | — |
| Qual a saúde financeira geral? | KPIs gerais | — |
| Receita e lucro estão crescendo? | Desempenho mensal (MoM) | — |
| Quais perfis de cliente gastam mais? | Segmentação por idade e fidelidade | — |
| Gênero influencia preferência de produto? | Preferências por gênero | — |
| Qual intensidade de cacau é mais rentável? | Produtos por cacau | — |
| Quais lojas merecem atenção? | Desempenho de lojas (tiers) | — |
| Descontos compensam em volume? | Impacto de descontos na margem | — |
| Há padrões sazonais consistentes? | Sazonalidade YoY | — |
| Quais cidades geram mais valor? | Desempenho por cidade | Barras (receita, lucro, volume) |
| Programa de fidelidade faz diferença? | Fidelidade vs não-membros | Barras (ticket médio, frequência) |
| Demanda varia por estação? | Top 10 produtos por estação | Linhas (flutuação sazonal) |
| Quando e quem compra mais? | Consumo por dia da semana | Linhas (gênero, faixa etária) |
| Existem perfis de consumidor distintos? | Clusterização K-Means | Dispersão (PCA) |
| Quando cada perfil é mais ativo? | Comportamento dos clusters | Linhas (volume por dia) |
| Receita e volume seguem tendência? | Tendência diária (média móvel 14d) | Linhas (eixo duplo) |
| Lucro acompanha crescimento de receita? | Correlação receita × lucro | Dispersão (tendência linear) |

## Stack

- **Ambiente:** Jupyter Notebook
- **Análise:** Pandas + NumPy
- **Visualização:** Matplotlib (notebook) / Plotly (dashboard)
- **Dashboard:** Streamlit
- **Banco de dados:** DuckDB
- **Controle de versão:** Git + GitHub

## Estrutura do repositório

```
├── data/
│   ├── chocolate_sales.db      # Banco DuckDB
│   └── basic_queries.ipynb     # Consultas auxiliares
├── src/
│   ├── helpers.py              # ConectorBD (abstração DuckDB)
│   ├── analysis.py             # Funções de análise exploratória
│   └── visualizations.py       # Funções de visualização (Matplotlib)
├── dashboard/
│   ├── app.py                  # Página inicial (Visão Geral)
│   ├── data.py                 # Acesso a dados e gráficos (com cache)
│   ├── charts.py               # Visualizações interativas (Plotly)
│   └── pages/                  # Páginas Clientes, Produtos, Lojas, Tendências
├── entregas.ipynb              # Notebook principal (entrega da 1.ª etapa)
├── pyproject.toml              # Dependências do projeto
├── requirements.txt            # Dependências de execução do dashboard
└── uv.lock                     # Lock de versões
```

## Como executar

1. Instale o [uv](https://github.com/astral-sh/uv) (gerenciador de pacotes Python)
2. Clone o repositório e entre na pasta do projeto
3. Execute `uv sync` para criar o ambiente virtual e instalar as dependências

**Notebook de análise (1.ª etapa):** abra `entregas.ipynb` no Jupyter e execute todas as células.

**Dashboard Streamlit (2.ª etapa):** execute `uv run streamlit run dashboard/app.py`.

## Equipe

- Fernanda Santos da Silva
- Gustavo Aquino de Oliveira
- Júlia Stefanni Muniz dos Santos
- Roberto Arede Rabelo Mendes
- Salvatore Gasparini Xerri
- Vitor Cristiano Dahmer
