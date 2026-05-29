from flask import Flask, request
import pyodbc

app = Flask(__name__)

conexao = pyodbc.connect(
    "driver={ODBC Driver 17 for SQL Server};"
    "server=DIOGO\\DMOR;"
    "database=master;"
    "trusted_connection=yes;"
)

cursor = conexao.cursor()


@app.route("/saldo", methods=["POST"])
def saldo():
    data = request.json
    qr = data["qr_code"]

    cursor.execute("SELECT saldo_credito FROM cliente WHERE qr_code = ?", (qr,))
    res = cursor.fetchone()

    if res:
        return f"Saldo: {res[0]}"
    return "Cliente não encontrado"


@app.route("/entrada", methods=["POST"])
def entrada():
    data = request.json
    qr = data["qr_code"]
    valor = float(data["valor"])

    cursor.execute("UPDATE cliente SET saldo_credito = saldo_credito + ? WHERE qr_code = ?", (valor, qr))
    conexao.commit()

    return "Crédito adicionado"


@app.route("/saida", methods=["POST"])
def saida():
    data = request.json
    qr = data["qr_code"]
    valor = float(data["valor"])

    cursor.execute("SELECT saldo_credito FROM cliente WHERE qr_code = ?", (qr,))
    res = cursor.fetchone()

    if res and res[0] >= valor:
        cursor.execute("UPDATE cliente SET saldo_credito = saldo_credito - ? WHERE qr_code = ?", (valor, qr))
        conexao.commit()
        return "Acesso liberado 🎢"

    return "Saldo insuficiente ❌"


app.run(debug=True)


@app.route("/saldo", methods=["POST"])
def saldo():
    data = request.json
    qr = data.get("qr_code")

    cursor.execute("SELECT saldo_credito FROM cliente WHERE qr_code = ?", (qr,))
    res = cursor.fetchone()

    if res:
        return str(res[0])  # 👈 importante retornar string simples
    return "Cliente não encontrado"

from flask import Flask, request, jsonify
import pyodbc

app = Flask(__name__)

conexao = pyodbc.connect(
    "driver={ODBC Driver 17 for SQL Server};"
    "server=DIOGO\\DMOR;"
    "database=master;"
    "trusted_connection=yes;"
)

cursor = conexao.cursor()

# VER SALDO
@app.route("/saldo", methods=["POST"])
def saldo():
    data = request.json
    qr = data.get("qr_code")

    cursor.execute("SELECT saldo_credito FROM cliente WHERE qr_code = ?", (qr,))
    res = cursor.fetchone()

    if res:
        return jsonify({"status": "ok", "saldo": float(res[0])})
    return jsonify({"status": "erro", "msg": "Cliente não encontrado"})

# ADICIONAR CRÉDITO
@app.route("/entrada", methods=["POST"])
def entrada():
    data = request.json
    qr = data.get("qr_code")
    valor = float(data.get("valor", 0))

    cursor.execute("UPDATE cliente SET saldo_credito = saldo_credito + ? WHERE qr_code = ?", (valor, qr))
    conexao.commit()

    return jsonify({"status": "ok", "msg": "Crédito adicionado"})

# USAR CRÉDITO
@app.route("/saida", methods=["POST"])
def saida():
    data = request.json
    qr = data.get("qr_code")
    valor = float(data.get("valor", 0))

    cursor.execute("SELECT saldo_credito FROM cliente WHERE qr_code = ?", (qr,))
    res = cursor.fetchone()

    if res and res[0] >= valor:
        cursor.execute("UPDATE cliente SET saldo_credito = saldo_credito - ? WHERE qr_code = ?", (valor, qr))
        conexao.commit()
        return jsonify({"status": "ok", "msg": "Acesso liberado 🎢"})
    
    return jsonify({"status": "erro", "msg": "Saldo insuficiente ❌"})

app.run(debug=True)

from flask import Flask, request, jsonify
from flask_cors import CORS
import pyodbc

app = Flask(__name__)
CORS(app)  # 👈 ISSO LIBERA O FRONT

conexao = pyodbc.connect(
    "driver={ODBC Driver 17 for SQL Server};"
    "server=DIOGO\\DMOR;"
    "database=master;"
    "trusted_connection=yes;"
)

cursor = conexao.cursor()




