import pandas as pd
import numpy as np
from .helpers import ConectorBD

def verificar_qualidade_dados(conector):
    """
    Verifica a qualidade das quatro tabelas principais do dataset.
    Retorna um Styler do Pandas que renderiza como tabela HTML colorida no Jupyter,
    destacando em vermelho as colunas com valores nulos.
    """
    df_vendas   = conector.obter_tabela_bruta('sales')
    df_clientes = conector.obter_tabela_bruta('customers')
    df_produtos = conector.obter_tabela_bruta('products')
    df_lojas    = conector.obter_tabela_bruta('stores')

    tabelas = {
        'Vendas':   df_vendas,
        'Clientes': df_clientes,
        'Produtos': df_produtos,
        'Lojas':    df_lojas,
    }

    linhas = []
    for nome, df in tabelas.items():
        total = len(df)
        duplicatas = df.duplicated().sum()
        for coluna in df.columns:
            nulos = df[coluna].isnull().sum()
            linhas.append({
                'Tabela':         nome,
                'Coluna':         coluna,
                'Total registros': total,
                'Nulos':          nulos,
                'Nulos (%)':      round(nulos / total * 100, 2),
                'Duplicatas':     duplicatas,
            })

    df_relatorio = pd.DataFrame(linhas)

    def destacar_nulos(val):
        return 'background-color: #ffd6d6; color: #900' if val > 0 else ''

    return (
        df_relatorio.style
        .map(destacar_nulos, subset=['Nulos', 'Nulos (%)'])
        .format({'Nulos (%)': '{:.2f}%', 'Total registros': '{:,}', 'Duplicatas': '{:,}'})
        .set_caption('Relatório de Qualidade dos Dados')
        .set_table_styles([
            {'selector': 'caption',
             'props': 'font-size: 14px; font-weight: bold; text-align: left; padding-bottom: 8px;'},
            {'selector': 'thead th',
             'props': 'background-color: #f0f0f0; font-weight: bold; text-align: center;'},
            {'selector': 'tbody tr:nth-child(even)',
             'props': 'background-color: #fafafa;'},
        ])
        .hide(axis='index')
    )

def calcular_kpis_gerais(conector):
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
    df['crescimento_receita_mom_pct'] = df.groupby('ano')['receita_total'].pct_change() * 100
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
    limites = [18, 30, 45, 60, np.inf]
    rotulos = ['18-29', '30-44', '45-59', '60+']
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
    (df_chocolate['cocoa_percent'] <= 60),
    (df_chocolate['cocoa_percent'] <= 70),
    (df_chocolate['cocoa_percent'] > 70)
    ]
    escolhas = ['Intensidade Baixa (≤60%)', 'Meio Amargo (61-70%)', 'Amargo (>70%)']
    df_chocolate['intensidade_cacau'] = np.select(condicoes, escolhas, default='Desconhecido')
    
    # Agrupando pela nova métrica de intensidade
    metricas_intensidade = df_chocolate.groupby('intensidade_cacau').agg(
        lucro_total=('lucro_total', 'sum'),
        volume_total=('volume_total', 'sum')
    ).reset_index()
    
    return df_produtos, metricas_intensidade

def analisar_desempenho_lojas(conector):
    """
    Analisa o desempenho comparativo entre lojas usando o ConectorBD.

    Cruza a tabela fato 'sales' com a dimensão 'stores' para calcular as
    principais métricas de negócio por loja: receita, lucro, volume e margem.
    Também classifica cada loja em um tier de desempenho usando np.select,
    facilitando a identificação de lojas que merecem atenção estratégica.

    Retorna
    -------
    df_lojas : pd.DataFrame
        Métricas agregadas por loja, ordenadas por lucro total decrescente.
        Colunas: store_id, (colunas da tabela stores), receita_total,
                 custo_total, lucro_total, itens_vendidos, margem_lucro_pct,
                 ticket_medio, tier_desempenho.
    """
    df = conector.obter_vendas_com_dimensao('stores', 'store_id')

    # Agrega as métricas principais por loja com Pandas
    df_lojas = df.groupby(['store_id']).agg(
        receita_total=('revenue', 'sum'),
        custo_total=('cost', 'sum'),
        lucro_total=('profit', 'sum'),
        itens_vendidos=('quantity', 'sum'),
        total_pedidos=('order_id', 'count')
    ).reset_index()

    # Enriquece com métricas derivadas
    df_lojas['margem_lucro_pct'] = (
        df_lojas['lucro_total'] / df_lojas['receita_total'] * 100
    ).round(2)

    df_lojas['ticket_medio'] = (
        df_lojas['receita_total'] / df_lojas['total_pedidos']
    ).round(2)

    # Classifica lojas em tiers usando percentis de lucro (NumPy)
    p33 = np.percentile(df_lojas['lucro_total'], 33)
    p66 = np.percentile(df_lojas['lucro_total'], 66)

    condicoes_tier = [
        df_lojas['lucro_total'] >= p66,
        df_lojas['lucro_total'] >= p33,
        df_lojas['lucro_total'] < p33,
    ]
    tiers = ['Alto desempenho', 'Desempenho médio', 'Baixo desempenho']
    df_lojas['tier_desempenho'] = np.select(condicoes_tier, tiers, default='')

    # Traz as colunas descritivas da tabela de lojas (nome, cidade, país etc.)
    colunas_loja = [c for c in df.columns if c not in
                    ['order_id', 'revenue', 'cost', 'profit', 'quantity',
                     'discount', 'order_date', 'customer_id', 'product_id']]
    info_lojas = df[colunas_loja].drop_duplicates(subset='store_id')

    df_lojas = info_lojas.merge(df_lojas, on='store_id')
    df_lojas = df_lojas.sort_values('lucro_total', ascending=False).reset_index(drop=True)

    return df_lojas


def analisar_impacto_desconto(conector):
    """
    Investiga se a política de descontos é financeiramente saudável para o negócio.

    Categoriza cada venda por faixa de desconto e calcula, para cada faixa,
    a margem de lucro real e o volume gerado. O objetivo é responder se o
    desconto compensa em volume ou corrói a margem sem retorno proporcional.

    Retorna
    -------
    df_faixas : pd.DataFrame
        Análise por faixa de desconto.
        Colunas: faixa_desconto, total_vendas, receita_total, lucro_total,
                 margem_media_pct, volume_total, receita_media_por_venda.

    df_correlacao : pd.DataFrame
        Estatísticas descritivas de NumPy para suportar uma análise de
        correlação entre desconto e margem.
        Colunas: metrica, valor.
    """
    df = conector.obter_tabela_bruta('sales')

    # Converte desconto de decimal para percentual inteiro
    df['desconto_pct'] = (df['discount'] * 100).round(0).astype(int)
    df['margem_pct'] = (df['profit'] / df['revenue'] * 100).round(2)

    # Cria faixas de desconto com pd.cut
    limites = [-1, 0, 5, 10, 15, 20]
    rotulos = ['Sem desconto', '1–5%', '6–10%', '11–15%', '16–20%']
    df['faixa_desconto'] = pd.cut(
        df['desconto_pct'], bins=limites, labels=rotulos, right=True
    )

    # Agrega por faixa
    df_faixas = df.groupby('faixa_desconto', observed=True).agg(
        total_vendas=('order_id', 'count'),
        receita_total=('revenue', 'sum'),
        lucro_total=('profit', 'sum'),
        volume_total=('quantity', 'sum'),
        margem_media_pct=('margem_pct', 'mean'),
    ).reset_index()

    df_faixas['receita_media_por_venda'] = (
        df_faixas['receita_total'] / df_faixas['total_vendas']
    ).round(2)
    df_faixas['margem_media_pct'] = df_faixas['margem_media_pct'].round(2)

    # Estatísticas de correlação com NumPy
    # Usa os valores individuais de desconto e margem (não as faixas agregadas)
    correlacao = np.corrcoef(df['desconto_pct'], df['margem_pct'])[0, 1]
    desconto_sem = df.loc[df['desconto_pct'] == 0, 'margem_pct'].mean()
    desconto_com = df.loc[df['desconto_pct'] > 0, 'margem_pct'].mean()
    impacto_margem = desconto_com - desconto_sem

    df_correlacao = pd.Series({
        'Correlação desconto × margem': f"{correlacao:.4f}",
        'Margem média sem desconto': f"{desconto_sem:.2f}%",
        'Margem média com desconto': f"{desconto_com:.2f}%",
        'Impacto médio do desconto na margem': f"{impacto_margem:.2f} p.p.",
        'Total de vendas com desconto': f"{(df['desconto_pct'] > 0).sum():,}".replace(',', '.'),
        'Total de vendas sem desconto': f"{(df['desconto_pct'] == 0).sum():,}".replace(',', '.'),
    }, name='Impacto dos Descontos')

    return df_faixas, df_correlacao


def analisar_preferencias_por_genero(conector):
    """
    Cruza dados demográficos (gênero) com preferências de produto para
    identificar padrões de consumo distintos entre grupos de clientes.

    Usa o ConectorBD para realizar dois JOINs encadeados (clientes + vendas +
    produtos) via consulta personalizada, e aplica Pandas para calcular
    a distribuição de preferências de categoria e intensidade de cacau por gênero.

    Retorna
    -------
    df_categoria : pd.DataFrame
        Distribuição de receita e volume por gênero e categoria de produto.
        Colunas: gender, category, receita_total, volume_total,
                 pct_receita_no_genero.

    df_cacau : pd.DataFrame
        Distribuição de receita e volume por gênero e intensidade de cacau.
        Colunas: gender, intensidade_cacau, receita_total, volume_total,
                 pct_receita_no_genero.
    """
    # Requer JOIN triplo — usa consulta personalizada do conector
    consulta = """
        SELECT
            c.gender,
            p.category,
            p.cocoa_percent,
            s.revenue,
            s.quantity,
            s.profit
        FROM sales s
        JOIN customers c ON s.customer_id = c.customer_id
        JOIN products p  ON s.product_id  = p.product_id
        WHERE c.gender IS NOT NULL
    """
    df = conector.executar_consulta_personalizada(consulta)

    # --- Análise por categoria de produto ---
    df_categoria = df.groupby(['gender', 'category']).agg(
        receita_total=('revenue', 'sum'),
        volume_total=('quantity', 'sum'),
    ).reset_index()

    # Calcula participação percentual da categoria dentro de cada gênero
    total_por_genero = df_categoria.groupby('gender')['receita_total'].transform('sum')
    df_categoria['pct_receita_no_genero'] = (
        df_categoria['receita_total'] / total_por_genero * 100
    ).round(2)

    df_categoria = df_categoria.sort_values(
        ['gender', 'receita_total'], ascending=[True, False]
    ).reset_index(drop=True)

    # --- Análise por intensidade de cacau ---
    df_cacau_raw = df[df['cocoa_percent'].notna()].copy()

    # Reutiliza a mesma lógica de categorização de intensidade de analysis.py
    condicoes = [
        (df_cacau_raw['cocoa_percent'] <= 60),
        (df_cacau_raw['cocoa_percent'] <= 70),
        (df_cacau_raw['cocoa_percent'] > 70),
    ]
    escolhas = ['Intensidade Baixa (≤60%)', 'Meio Amargo (61–70%)', 'Amargo (>70%)']
    df_cacau_raw['intensidade_cacau'] = np.select(condicoes, escolhas, default='Desconhecido')

    df_cacau = df_cacau_raw.groupby(['gender', 'intensidade_cacau']).agg(
        receita_total=('revenue', 'sum'),
        volume_total=('quantity', 'sum'),
    ).reset_index()

    total_por_genero_cacau = df_cacau.groupby('gender')['receita_total'].transform('sum')
    df_cacau['pct_receita_no_genero'] = (
        df_cacau['receita_total'] / total_por_genero_cacau * 100
    ).round(2)

    df_cacau = df_cacau.sort_values(
        ['gender', 'receita_total'], ascending=[True, False]
    ).reset_index(drop=True)

    return df_categoria, df_cacau


def analisar_sazonalidade_yoy(conector):
    """
    Compara o desempenho dos mesmos meses entre 2023 e 2024 (análise YoY —
    Year over Year), revelando padrões sazonais consistentes que a análise
    MoM (mês a mês) não captura.

    A análise MoM existente em obter_desempenho_mensal_vendas é útil para
    detectar aceleração/desaceleração de curto prazo, mas confunde variação
    sazonal com tendência real. A análise YoY isola os dois efeitos.

    Retorna
    -------
    df_pivot : pd.DataFrame
        Tabela pivotada com receita mensal por ano, crescimento YoY e
        classificação de sazonalidade.
        Colunas: mes, receita_2023, receita_2024, variacao_yoy_pct,
                 padrao_sazonal.

    df_estatisticas : pd.Series
        Estatísticas descritivas da sazonalidade com NumPy.
    """
    consulta = """
        SELECT
            c.year  AS ano,
            c.month AS mes,
            SUM(s.revenue) AS receita_total,
            SUM(s.profit)  AS lucro_total,
            SUM(s.quantity) AS itens_vendidos
        FROM sales s
        JOIN calendar c ON s.order_date = c.date
        GROUP BY 1, 2
        ORDER BY 1, 2
    """
    df = conector.executar_consulta_personalizada(consulta)

    # Pivota para ter um ano por coluna — facilita o cálculo YoY
    df_pivot = df.pivot(index='mes', columns='ano', values='receita_total').reset_index()
    df_pivot.columns.name = None

    anos = sorted(df['ano'].unique())
    if len(anos) >= 2:
        ano_base, ano_atual = anos[0], anos[1]
        col_base = ano_base
        col_atual = ano_atual

        df_pivot = df_pivot.rename(columns={
            col_base: f'receita_{ano_base}',
            col_atual: f'receita_{ano_atual}',
        })

        col_b = f'receita_{ano_base}'
        col_a = f'receita_{ano_atual}'

        # Crescimento YoY com Pandas
        df_pivot['variacao_yoy_pct'] = (
            (df_pivot[col_a] - df_pivot[col_b]) / df_pivot[col_b] * 100
        ).round(2)

        # Classifica padrão sazonal usando np.select
        media_yoy = df_pivot['variacao_yoy_pct'].mean()
        desvio_yoy = df_pivot['variacao_yoy_pct'].std()

        condicoes_sazo = [
            df_pivot['variacao_yoy_pct'] > media_yoy + desvio_yoy,
            df_pivot['variacao_yoy_pct'] < media_yoy - desvio_yoy,
        ]
        padroes = ['Sazonalidade positiva', 'Sazonalidade negativa']
        df_pivot['padrao_sazonal'] = np.select(
            condicoes_sazo, padroes, default='Comportamento estável'
        )

        # Estatísticas descritivas com NumPy
        variacoes = df_pivot['variacao_yoy_pct'].values
        df_estatisticas = pd.Series({
            'Crescimento YoY médio':        f"{np.mean(variacoes):.2f}%",
            'Melhor mês (maior crescimento YoY)':
                f"Mês {df_pivot.loc[df_pivot['variacao_yoy_pct'].idxmax(), 'mes']:.0f} "
                f"({np.max(variacoes):.2f}%)",
            'Pior mês (menor crescimento YoY)':
                f"Mês {df_pivot.loc[df_pivot['variacao_yoy_pct'].idxmin(), 'mes']:.0f} "
                f"({np.min(variacoes):.2f}%)",
            'Meses com crescimento positivo':
                str(int(np.sum(variacoes > 0))),
            'Meses com crescimento negativo':
                str(int(np.sum(variacoes < 0))),
            'Desvio padrão das variações YoY': f"{np.std(variacoes):.2f} p.p.",
        }, name='Sazonalidade Year-over-Year')

    return df_pivot, df_estatisticas