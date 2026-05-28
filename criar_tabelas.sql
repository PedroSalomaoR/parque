-- Execute este script no painel do PostgreSQL do Render
-- Dashboard → seu banco → "Query" ou via psql

CREATE TABLE IF NOT EXISTS cliente (
    cliente_id    SERIAL        PRIMARY KEY,
    nome          VARCHAR(100)  NOT NULL,
    qr_code       VARCHAR(255)  UNIQUE NOT NULL,
    saldo_credito DECIMAL(10,2) DEFAULT 0.00,
    catraca       BOOLEAN       DEFAULT FALSE,
    data_cadastro TIMESTAMP     DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS transacao (
    transacao_id SERIAL        PRIMARY KEY,
    cliente_id   INT           NOT NULL,
    tipo         VARCHAR(10)   NOT NULL CHECK (tipo IN ('entrada', 'saida')),
    valor        DECIMAL(10,2) NOT NULL,
    data         TIMESTAMP     DEFAULT NOW(),
    FOREIGN KEY (cliente_id) REFERENCES cliente(cliente_id)
);
