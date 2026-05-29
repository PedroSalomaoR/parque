import pyodbc

conn = pyodbc.connect(
    "driver={ODBC Driver 17 for SQL Server};"
    "server=localhost\\SQLEXPRESS;"
    "trusted_connection=yes;"
)
cursor = conn.cursor()

try:
    # 1. Primeiro deleta as tabelas filhas (que referenciam cliente)
    cursor.execute("DELETE FROM transacao")
    print(f"{cursor.rowcount} transações deletadas.")

    # 2. Depois deleta os clientes
    cursor.execute("DELETE FROM cliente")
    print(f"{cursor.rowcount} clientes deletados.")

    conn.commit()
    print("Limpeza concluída com sucesso!")

except Exception as e:
    conn.rollback()
    print(f"Erro: {e}")

finally:
    conn.close()