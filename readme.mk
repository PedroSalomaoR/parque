# 🎢 Parque Digital

Sistema de créditos para parque de diversões com QR Code, backend Flask e SQL Server.

---

## 📁 Estrutura

```
parque_digital/
├── app.py        ← Backend Flask (API REST)
├── index.html    ← Frontend (abrir direto no navegador)
├── banco.sql     ← Script SQL para criar as tabelas
└── README.md
```

---

## ⚙️ Pré-requisitos

- Python 3.8+
- SQL Server (local) com ODBC Driver 17
- SSMS para rodar o script SQL

---

## 🚀 Como rodar

### 1. Criar o banco de dados

Abra o **SSMS**, conecte em  e execute o arquivo `banco.sql`.

> Se quiser usar um banco dedicado (recomendado), descomente as linhas `CREATE DATABASE` e `USE` no topo do script, e atualize a string de conexão em `app.py`.

---

### 2. Instalar dependências Python

```bash
pip install flask flask-cors pyodbc
```

---

### 3. Configurar a conexão (se necessário)

Abra `app.py` e ajuste a função `get_conn()` se o servidor ou banco for diferente:

```python
def get_conn():
    return pyodbc.connect(
        "driver={ODBC Driver 17 for SQL Server};"
        "server=DIOGO\\DMOR;"   # ← seu servidor
        "database=master;"      # ← seu banco
        "trusted_connection=yes;"
    )
```

---

### 4. Iniciar o backend

```bash
python app.py
```

O servidor sobe em: `http://127.0.0.1:5000`

---

### 5. Abrir o frontend

Basta abrir o arquivo `index.html` direto no navegador (duplo clique).

> O frontend já aponta para `http://127.0.0.1:5000` — não precisa configurar nada.

---

## 🔌 Endpoints da API

| Método | Rota          | Descrição                          |
|--------|---------------|------------------------------------|
| POST   | `/saldo`      | Consulta saldo por QR Code         |
| POST   | `/entrada`    | Adiciona crédito                   |
| POST   | `/saida`      | Debita crédito (uso de atração)    |
| POST   | `/cadastrar`  | Cadastra novo cliente              |
| POST   | `/historico`  | Últimas 20 transações do cliente   |

### Exemplos de payload

**`/saldo`**
```json
{ "qr_code": "123ABC" }
```

**`/entrada`**
```json
{ "qr_code": "123ABC", "valor": 50 }
```

**`/saida`**
```json
{ "qr_code": "123ABC", "valor": 15 }
```

**`/cadastrar`**
```json
{ "nome": "Diogo", "qr_code": "123ABC" }
```

---

## 🧪 Dados de teste

Para inserir clientes de exemplo, descomente o bloco `INSERT` no final do `banco.sql` e execute novamente.

```sql
INSERT INTO cliente (nome, qr_code, saldo_credito) VALUES
    ('Diogo', '123ABC', 100.00),
    ('Maria', '456DEF',  50.00);
```

---

## 🎡 Atrações e preços

| Atração         | Preço  |
|-----------------|--------|
| Carrossel       | R$ 5   |
| Roda Gigante    | R$ 10  |
| Montanha Russa  | R$ 15  |
| Queda Livre     | R$ 20  |