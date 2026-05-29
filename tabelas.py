import pyodbc

conn = pyodbc.connect(
    "driver={ODBC Driver 17 for SQL Server};"
    "server=localhost\\SQLEXPRESS;"
    "trusted_connection=yes;"
)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE cliente (
    cliente_id    INT           PRIMARY KEY IDENTITY(1,1),
    nome          VARCHAR(100)  NOT NULL,
    qr_code       VARCHAR(255)  UNIQUE NOT NULL,
    saldo_credito DECIMAL(10,2) DEFAULT 0.00,
    catraca       BIT           DEFAULT 0,
    data_cadastro DATETIME      DEFAULT GETDATE()
)
""")

cursor.execute("""
CREATE TABLE transacao (
    transacao_id INT           PRIMARY KEY IDENTITY(1,1),
    cliente_id   INT           NOT NULL,
    tipo         VARCHAR(10)   NOT NULL CHECK (tipo IN ('entrada', 'saida')),
    valor        DECIMAL(10,2) NOT NULL,
    data         DATETIME      DEFAULT GETDATE(),
    FOREIGN KEY (cliente_id) REFERENCES cliente(cliente_id)
)
""")

conn.commit()
conn.close()
print("Tabelas criadas com sucesso!")