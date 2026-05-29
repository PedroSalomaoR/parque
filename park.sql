-- ================================================================
-- PARQUE DIGITAL — Script de criação do banco de dados
-- Execute no SQL Server Management Studio (SSMS)
-- Banco: master (ou crie um banco dedicado, ex: ParqueDigital)
-- ================================================================

-- Se quiser usar um banco dedicado, descomente as linhas abaixo:
-- CREATE DATABASE ParqueDigital;
-- GO
-- USE ParqueDigital;
-- GO

-- ── TABELA DE CLIENTES ──────────────────────────────────────────────
-- qr_code UNIQUE: cada pulseira/cartão é único
-- saldo_credito DECIMAL(10,2): precisão monetária, sem número quebrado
-- catraca BIT: flag de acesso liberado (0 = fechada, 1 = aberta)
-- data_cadastro: preenchida automaticamente

CREATE TABLE cliente (
    cliente_id    INT           PRIMARY KEY IDENTITY(1,1),
    nome          VARCHAR(100)  NOT NULL,
    qr_code       VARCHAR(255)  UNIQUE NOT NULL,
    saldo_credito DECIMAL(10,2) DEFAULT 0.00,
    catraca       BIT           DEFAULT 0,
    data_cadastro DATETIME      DEFAULT GETDATE()
);
GO

-- ── TABELA DE TRANSAÇÕES ────────────────────────────────────────────
-- tipo CHECK: só aceita 'entrada' ou 'saida'
-- data: preenchida automaticamente

CREATE TABLE transacao (
    transacao_id INT           PRIMARY KEY IDENTITY(1,1),
    cliente_id   INT           NOT NULL,
    tipo         VARCHAR(10)   NOT NULL CHECK (tipo IN ('entrada', 'saida')),
    valor        DECIMAL(10,2) NOT NULL,
    data         DATETIME      DEFAULT GETDATE(),

    FOREIGN KEY (cliente_id) REFERENCES cliente(cliente_id)
);
GO

-- ── DADOS DE TESTE ──────────────────────────────────────────────────
-- Descomente para inserir clientes de exemplo

/*
INSERT INTO cliente (nome, qr_code, saldo_credito) VALUES
    ('Diogo',   '123ABC', 100.00),
    ('Maria',   '456DEF',  50.00),
    ('Pedro',   '789GHI',  25.00);
*/

-- ── CONSULTAS ÚTEIS ─────────────────────────────────────────────────

-- Ver todos os clientes:
-- SELECT * FROM cliente;

-- Ver transações de um cliente:
-- SELECT c.nome, t.tipo, t.valor, t.data
-- FROM transacao t
-- JOIN cliente c ON c.cliente_id = t.cliente_id
-- WHERE c.qr_code = '123ABC'
-- ORDER BY t.data DESC;

-- Ranking de saldo:
-- SELECT TOP 10 nome, saldo_credito FROM cliente ORDER BY saldo_credito DESC;