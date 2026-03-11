import pandas as pd
import numpy as np
from .helpers import ConectorBD

def verificar_qualidade_dados(conector):
    """
    Extrai informações básicas e estatísticas descritivas das tabelas principais.
    Usa os métodos nativos do conector para puxar tabelas brutas e retorna
    uma Pandas Series formatada para exibição no Jupyter.
    """
    # Usando o conector para buscar os dados brutos necessários
    df_clientes = conector.obter_tabela_bruta('customers')
    df_vendas = conector.obter_tabela_bruta('sales')
    
    # Cálculos com NumPy e Pandas
    idade_media = np.mean(df_clientes['age'].dropna())
    idade_mediana = np.median(df_clientes['age'].dropna())
    receita_total = np.sum(df_vendas['revenue'])
    margem_media = np.mean(df_vendas['profit'] / df_vendas['revenue'])
    desconto_max = np.max(df_vendas['discount'])
    vendas_sem_desconto = len(df_vendas[df_vendas['discount'] == 0])

    # Criando um dicionário já formatado para negócios (Business Intelligence)
    relatorio_formatado = {
        'Idade Média dos Clientes': f"{idade_media:.1f} anos",
        'Idade Mediana dos Clientes': f"{idade_mediana:.0f} anos",
        'Receita Total Geral': f"$ {receita_total:,.2f}",
        'Margem de Lucro Média': f"{(margem_media * 100):.1f}%",
        'Desconto Máximo Oferecido': f"{(desconto_max * 100):.0f}%",
        'Quantidade de Vendas Sem Desconto': f"{vendas_sem_desconto:,}".replace(',', '.')
    }
    
    # Transformando em uma Série do Pandas para renderizar uma tabela bonita no Jupyter
    sr_qualidade = pd.Series(relatorio_formatado, name="Métricas Gerais de Negócio")
    
    return sr_qualidade

def obter_desempenho_mensal_vendas(conector: ConectorBD):
    """
    Analisa a tendência mensal usando a consulta personalizada do conector,
    e aplica cálculos de crescimento com Pandas.
    """
    consulta = """
        SELECT 
            c.year as ano, 
            c.month as mes, 
            SUM(s.revenue) as receita_total,
            SUM(s.cost) as custo_total,
            SUM(s.profit) as lucro_total,
            SUM(s.quantity) as itens_vendidos
        FROM sales s
        JOIN calendar c ON s.order_date = c.date
        GROUP BY 1, 2
        ORDER BY 1, 2
    """
    # Usando a flexibilidade do conector para queries complexas
    df = conector.executar_consulta_personalizada(consulta)
    
    # Engenharia de Recursos (Feature Engineering) com Pandas
    df['margem_lucro_pct'] = (df['lucro_total'] / df['receita_total']) * 100
    df['margem_lucro_pct'] = df['margem_lucro_pct'].round(2)
    
    # Calculando o crescimento da receita em relação ao mês anterior (MoM - Month over Month)
    df['crescimento_receita_mom_pct'] = df['receita_total'].pct_change() * 100
    df['crescimento_receita_mom_pct'] = df['crescimento_receita_mom_pct'].fillna(0).round(2)
    
    return df

def analisar_segmentacao_clientes(conector):
    """
    Usa o conector para mesclar Vendas e Clientes automaticamente.
    Trata a coluna binária de fidelidade, categoriza as idades e analisa o comportamento de compra.
    """
    # Conector faz o JOIN automaticamente
    df = conector.obter_vendas_com_dimensao('customers', 'customer_id')
    
    df['loyalty_member'] = df['loyalty_member'].map({1: 'Sim', 0: 'Não'})
    
    # Agrupando dados por cliente usando Pandas
    df_clientes = df.groupby(['customer_id', 'age', 'gender', 'loyalty_member']).agg(
        total_pedidos=('order_id', 'count'),
        gasto_total=('revenue', 'sum')
    ).reset_index()
    
    # Tratando valores nulos de idade com a mediana
    df_clientes['age'] = df_clientes['age'].fillna(df_clientes['age'].median())
    
    # Criando faixas etárias usando pd.cut
    limites = [0, 18, 30, 45, 60, 100]
    rotulos = ['<18', '18-29', '30-44', '45-59', '60+']
    df_clientes['faixa_etaria'] = pd.cut(df_clientes['age'], bins=limites, labels=rotulos, right=False)
    
    # Agrupando pelas novas faixas e pelo status de fidelidade
    analise_segmentos = df_clientes.groupby(['faixa_etaria', 'loyalty_member'])['gasto_total'].agg(
        media_gasto='mean', 
        soma_gasto='sum', 
        contagem_clientes='count'
    ).reset_index()
    
    return analise_segmentos

def analisar_produtos_cacau(conector: ConectorBD):
    """
    Usa o conector para mesclar Vendas e Produtos.
    Analisa a correlação entre a porcentagem de cacau e a lucratividade usando NumPy.
    """
    # Conector faz o JOIN automaticamente
    df = conector.obter_vendas_com_dimensao('products', 'product_id')
    
    # Agregando por produto usando Pandas
    df_produtos = df.groupby(['category', 'cocoa_percent']).agg(
        volume_total=('quantity', 'sum'),
        lucro_total=('profit', 'sum')
    ).reset_index()
    
    # Filtrando apenas produtos que contêm a especificação de cacau
    df_chocolate = df_produtos[df_produtos['cocoa_percent'].notna()].copy()
    
    # Criando métrica categórica de intensidade de cacau com NumPy
    condicoes = [
        (df_chocolate['cocoa_percent'] < 50),
        (df_chocolate['cocoa_percent'] >= 50) & (df_chocolate['cocoa_percent'] <= 70),
        (df_chocolate['cocoa_percent'] > 70)
    ]
    escolhas = ['Ao Leite / Baixo Cacau', 'Meio Amargo (50-70%)', 'Amargo (>70%)']
    df_chocolate['intensidade_cacau'] = np.select(condicoes, escolhas, default='Desconhecido')
    
    # Agrupando pela nova métrica de intensidade
    metricas_intensidade = df_chocolate.groupby('intensidade_cacau').agg(
        lucro_total=('lucro_total', 'sum'),
        volume_total=('volume_total', 'sum')
    ).reset_index()
    
    return df_produtos, metricas_intensidade