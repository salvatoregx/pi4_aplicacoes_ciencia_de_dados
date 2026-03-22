import duckdb
import pandas as pd

db_path = "data/chocolate_sales.db"

# Conectar ao DuckDB
conn = duckdb.connect(db_path)

# Listar tabelas
tabelas = conn.execute("SHOW TABLES").fetchall()

print("📊 Tabelas encontradas:\n")
for tabela in tabelas:
    print("-", tabela[0])

print("\n🔎 Prévia dos dados:\n")

# Mostrar conteúdo
for tabela in tabelas:
    nome_tabela = tabela[0]
    print(f"===== {nome_tabela} =====")
    
    df = conn.execute(f"SELECT * FROM {nome_tabela} LIMIT 50").df()
    print(df)
    print()

conn.close()