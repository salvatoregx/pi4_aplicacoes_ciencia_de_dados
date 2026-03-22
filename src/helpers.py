import duckdb
from pathlib import Path

class ConectorBD:
    """Conector DuckDB que retorna DataFrames do Pandas."""
    
    def __init__(self, caminho_bd=None):
        if caminho_bd is None:
            # Descobre dinamicamente a raiz do projeto.
            # Path(__file__) é o src/helpers.py. O .parent.parent volta para a raiz do projeto.
            pasta_raiz = Path(__file__).parent.parent
            
            # Constrói o caminho absoluto: /.../pi4_aplicacoes_ciencia_de_dados/data/chocolate_sales.db
            self.caminho_bd = str(pasta_raiz / 'data' / 'chocolate_sales.db')
        else:
            self.caminho_bd = caminho_bd

    def _executar_consulta(self, consulta):
        with duckdb.connect(self.caminho_bd) as conexao:
            df = conexao.execute(consulta).df()
        return df

    def obter_tabela_bruta(self, nome_tabela, limite=None):
        """Retorna a tabela completa (ou limitada) como DataFrame."""
        consulta = f"SELECT * FROM {nome_tabela}"
        if limite:
            consulta += f" LIMIT {limite}"
        return self._executar_consulta(consulta)

    def obter_vendas_com_dimensao(self, tabela_dimensao, chave_juncao):
        """JOIN de sales com a tabela dimensão informada."""
        consulta = f"""
            SELECT s.*, d.* EXCLUDE ({chave_juncao})
            FROM sales s
            JOIN {tabela_dimensao} d ON s.{chave_juncao} = d.{chave_juncao}
        """
        return self._executar_consulta(consulta)

    def obter_agregacao_vendas(self, tabela_dimensao, chave_juncao, coluna_agrupamento):
        """Métricas de vendas agregadas pela coluna de agrupamento."""
        consulta = f"""
            SELECT 
                d.{coluna_agrupamento},
                SUM(s.quantity) as total_unidades_vendidas,
                SUM(s.revenue) as receita_total,
                SUM(s.profit) as lucro_total,
                AVG(s.discount) as media_desconto_aplicado
            FROM sales s
            JOIN {tabela_dimensao} d ON s.{chave_juncao} = d.{chave_juncao}
            GROUP BY 1
            ORDER BY receita_total DESC
        """
        return self._executar_consulta(consulta)

    def obter_vendas_serie_temporal(self, granularidade_tempo='month'):
        """Vendas agregadas por granularidade temporal (day, week, month, year)."""
        granularidades_validas = ['year', 'month', 'week', 'day']
        if granularidade_tempo not in granularidades_validas:
            raise ValueError(f"A variável granularidade_tempo deve ser uma das opções: {granularidades_validas}")
            
        consulta = f"""
            SELECT 
                c.{granularidade_tempo},
                SUM(s.revenue) as receita_total,
                SUM(s.profit) as lucro_total
            FROM sales s
            JOIN calendar c ON s.order_date = c.date
            GROUP BY 1
            ORDER BY 1
        """
        return self._executar_consulta(consulta)

    def executar_consulta_personalizada(self, sql_personalizado):
        """Executa SQL arbitrário e retorna DataFrame."""
        return self._executar_consulta(sql_personalizado)