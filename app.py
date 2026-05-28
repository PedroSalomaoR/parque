from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import psycopg2
import os
import uuid

app = Flask(__name__)
CORS(app)

# ── CONEXÃO ──────────────────────────────────────────────────────────
def get_conn():
    return psycopg2.connect(os.environ["DATABASE_URL"])

# ── HELPER ───────────────────────────────────────────────────────────
def buscar_cliente(cursor, qr_code):
    cursor.execute(
        "SELECT cliente_id, nome, saldo_credito FROM cliente WHERE qr_code = %s",
        (qr_code,)
    )
    return cursor.fetchone()

# ── ROTAS DE ARQUIVOS ─────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route("/")
def root():
    return send_from_directory(BASE_DIR, "login.html")

@app.route("/login.html")
def login_page():
    return send_from_directory(BASE_DIR, "login.html")

@app.route("/index.html")
def index():
    return send_from_directory(BASE_DIR, "index.html")

@app.route("/cliente.html")
def cliente_page():
    return send_from_directory(BASE_DIR, "cliente.html")

# ── SALDO ─────────────────────────────────────────────────────────────
@app.route("/saldo", methods=["POST"])
def saldo():
    data = request.get_json()
    qr = data.get("qr_code", "").strip()
    if not qr:
        return jsonify({"status": "erro", "msg": "QR Code não informado."}), 400

    conn = None
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cliente = buscar_cliente(cursor, qr)
        if not cliente:
            return jsonify({"status": "erro", "msg": "Cliente não encontrado. ❌"}), 404
        cliente_id, nome, saldo = cliente
        return jsonify({"status": "ok", "nome": nome, "saldo": float(saldo)})
    except Exception as e:
        return jsonify({"status": "erro", "msg": f"Erro interno: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()

# ── ENTRADA ───────────────────────────────────────────────────────────
@app.route("/entrada", methods=["POST"])
def entrada():
    data = request.get_json()
    qr   = data.get("qr_code", "").strip()
    valor = data.get("valor")
    if not qr:
        return jsonify({"status": "erro", "msg": "QR Code não informado."}), 400
    try:
        valor = float(valor)
        if valor <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"status": "erro", "msg": "Valor inválido."}), 400

    conn = None
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cliente = buscar_cliente(cursor, qr)
        if not cliente:
            return jsonify({"status": "erro", "msg": "Cliente não encontrado. ❌"}), 404
        cliente_id, nome, saldo = cliente
        saldo = float(saldo)
        cursor.execute(
            "UPDATE cliente SET saldo_credito = saldo_credito + %s WHERE cliente_id = %s",
            (valor, cliente_id)
        )
        cursor.execute(
            "INSERT INTO transacao (cliente_id, tipo, valor) VALUES (%s, 'entrada', %s)",
            (cliente_id, valor)
        )
        conn.commit()
        return jsonify({
            "status": "ok",
            "msg": f"R$ {valor:.2f} adicionados com sucesso! 💰",
            "saldo": saldo + valor,
            "nome": nome
        })
    except Exception as e:
        return jsonify({"status": "erro", "msg": f"Erro interno: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()

# ── SAIDA ─────────────────────────────────────────────────────────────
@app.route("/saida", methods=["POST"])
def saida():
    data  = request.get_json()
    qr    = data.get("qr_code", "").strip()
    valor = data.get("valor")
    if not qr:
        return jsonify({"status": "erro", "msg": "QR Code não informado."}), 400
    try:
        valor = float(valor)
        if valor <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"status": "erro", "msg": "Valor inválido."}), 400

    conn = None
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cliente = buscar_cliente(cursor, qr)
        if not cliente:
            return jsonify({"status": "erro", "msg": "Cliente não encontrado. ❌"}), 404
        cliente_id, nome, saldo = cliente
        saldo = float(saldo)
        if saldo < valor:
            return jsonify({
                "status": "erro",
                "msg": f"Saldo insuficiente. Saldo atual: R$ {saldo:.2f} ❌"
            }), 400
        cursor.execute(
            "UPDATE cliente SET saldo_credito = saldo_credito - %s WHERE cliente_id = %s",
            (valor, cliente_id)
        )
        cursor.execute(
            "INSERT INTO transacao (cliente_id, tipo, valor) VALUES (%s, 'saida', %s)",
            (cliente_id, valor)
        )
        conn.commit()
        return jsonify({
            "status": "ok",
            "msg": "Acesso liberado! Aproveite a atração! 🎢",
            "saldo": float(saldo - valor),
            "nome": nome
        })
    except Exception as e:
        return jsonify({"status": "erro", "msg": f"Erro interno: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()

# ── CADASTRAR ─────────────────────────────────────────────────────────
@app.route("/cadastrar", methods=["POST"])
def cadastrar():
    data = request.get_json()
    nome = data.get("nome", "").strip()

    if not nome:
        return jsonify({"status": "erro", "msg": "Nome é obrigatório."}), 400

    qr = "PX-" + uuid.uuid4().hex[:8].upper()

    conn = None
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO cliente (nome, qr_code) VALUES (%s, %s)",
            (nome, qr)
        )
        conn.commit()
        return jsonify({
            "status": "ok",
            "msg": f"Cliente '{nome}' cadastrado com sucesso! ✅",
            "qr_code": qr
        })
    except psycopg2.errors.UniqueViolation:
        return jsonify({"status": "erro", "msg": "Erro ao gerar QR Code único. Tente novamente."}), 409
    except Exception as e:
        return jsonify({"status": "erro", "msg": f"Erro interno: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()

# ── HISTÓRICO ─────────────────────────────────────────────────────────
@app.route("/historico", methods=["POST"])
def historico():
    data = request.get_json()
    qr   = data.get("qr_code", "").strip()
    if not qr:
        return jsonify({"status": "erro", "msg": "QR Code não informado."}), 400

    conn = None
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cliente = buscar_cliente(cursor, qr)
        if not cliente:
            return jsonify({"status": "erro", "msg": "Cliente não encontrado. ❌"}), 404
        cliente_id, nome, saldo = cliente
        cursor.execute("""
            SELECT tipo, valor, data
            FROM transacao
            WHERE cliente_id = %s
            ORDER BY data DESC
            LIMIT 20
        """, (cliente_id,))
        transacoes = [
            {"tipo": row[0], "valor": float(row[1]), "data": str(row[2])}
            for row in cursor.fetchall()
        ]
        return jsonify({
            "status": "ok",
            "nome": nome,
            "saldo": float(saldo),
            "transacoes": transacoes
        })
    except Exception as e:
        return jsonify({"status": "erro", "msg": f"Erro interno: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()

# ── START ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
