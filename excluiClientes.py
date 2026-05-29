import pyodbc

conn = pyodbc.connect(
    "driver={ODBC Driver 17 for SQL Server};"
    "server=localhost\\SQLEXPRESS;"
    "trusted_connection=yes;"
)
cursor = conn.cursor()

qr = input("Digite o QR Code do cliente a deletar: ")

# deleta transações primeiro (por causa do FOREIGN KEY)
cursor.execute("DELETE FROM transacao WHERE cliente_id = (SELECT cliente_id FROM cliente WHERE qr_code = ?)", (qr,))
cursor.execute("DELETE FROM cliente WHERE qr_code = ?", (qr,))

conn.commit()
print(f"Cliente '{qr}' deletado com sucesso!")
conn.close()