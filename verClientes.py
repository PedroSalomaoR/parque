import pyodbc

conn = pyodbc.connect(
    "driver={ODBC Driver 17 for SQL Server};"
    "server=localhost\\SQLEXPRESS;"
    "trusted_connection=yes;"
)
cursor = conn.cursor()
cursor.execute("SELECT cliente_id, nome, qr_code, saldo_credito, data_cadastro FROM cliente")

for row in cursor.fetchall():
    print(f"ID: {row.cliente_id} | Nome: {row.nome} | QR: {row.qr_code} | Saldo: R$ {row.saldo_credito} | Cadastro: {row.data_cadastro}")

conn.close()