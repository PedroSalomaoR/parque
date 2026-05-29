from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pyodbc
import os
import uuid

app = Flask(__name__)
CORS(app)

def get_conn():
    return pyodbc.connect(
        "driver={ODBC Driver 17 for SQL Server};"
        "server=localhost\\SQLEXPRESS;"
        "trusted_connection=yes;"
    )

def buscar_cliente(cursor, qr_code):
    cursor.execute(
        "SELECT cliente_id, nome, saldo_credito FROM cliente WHERE qr_code = ?",
        (qr_code,)
    )
    return cursor.fetchone()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ── PÁGINAS ───────────────────────────────────────────────────────────
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

# ── OPERAÇÕES BÁSICAS ────────────────────────────────────────────────
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
        if conn: conn.close()


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
            "UPDATE cliente SET saldo_credito = saldo_credito + ? WHERE cliente_id = ?",
            (valor, cliente_id)
        )
        cursor.execute(
            "INSERT INTO transacao (cliente_id, tipo, valor) VALUES (?, 'entrada', ?)",
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
        if conn: conn.close()


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
            "UPDATE cliente SET saldo_credito = saldo_credito - ? WHERE cliente_id = ?",
            (valor, cliente_id)
        )
        cursor.execute(
            "INSERT INTO transacao (cliente_id, tipo, valor) VALUES (?, 'saida', ?)",
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
        if conn: conn.close()


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
            "INSERT INTO cliente (nome, qr_code) VALUES (?, ?)",
            (nome, qr)
        )
        conn.commit()
        return jsonify({
            "status": "ok",
            "msg": f"Cliente '{nome}' cadastrado com sucesso! ✅",
            "qr_code": qr
        })
    except pyodbc.IntegrityError:
        return jsonify({"status": "erro", "msg": "Erro ao gerar QR Code único. Tente novamente."}), 409
    except Exception as e:
        return jsonify({"status": "erro", "msg": f"Erro interno: {str(e)}"}), 500
    finally:
        if conn: conn.close()


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
            SELECT TOP 20 tipo, valor, data
            FROM transacao
            WHERE cliente_id = ?
            ORDER BY data DESC
        """, (cliente_id,))
        transacoes = [
            {"tipo": row.tipo, "valor": float(row.valor), "data": str(row.data)}
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
        if conn: conn.close()


# ── CLIENTES ─────────────────────────────────────────────────────────
@app.route("/clientes", methods=["GET"])
def listar_clientes():
    conn = None
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT cliente_id, nome, qr_code, saldo_credito, data_cadastro FROM cliente ORDER BY nome")
        clientes = [
            {
                "cliente_id": row.cliente_id,
                "nome": row.nome,
                "qr_code": row.qr_code,
                "saldo_credito": float(row.saldo_credito),
                "data_cadastro": str(row.data_cadastro)
            }
            for row in cursor.fetchall()
        ]
        return jsonify({"status": "ok", "clientes": clientes})
    except Exception as e:
        return jsonify({"status": "erro", "msg": str(e)}), 500
    finally:
        if conn: conn.close()


@app.route("/deletar", methods=["POST"])
def deletar_cliente():
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
            return jsonify({"status": "erro", "msg": "Cliente não encontrado."}), 404
        cliente_id, nome, _ = cliente
        cursor.execute("DELETE FROM transacao WHERE cliente_id = ?", (cliente_id,))
        cursor.execute("DELETE FROM cliente WHERE cliente_id = ?", (cliente_id,))
        conn.commit()
        return jsonify({"status": "ok", "msg": f"Cliente '{nome}' removido com sucesso."})
    except Exception as e:
        return jsonify({"status": "erro", "msg": str(e)}), 500
    finally:
        if conn: conn.close()


# ── TRANSAÇÕES ────────────────────────────────────────────────────────
@app.route("/todas_transacoes", methods=["GET"])
def todas_transacoes():
    conn = None
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT TOP 200 t.transacao_id, c.nome, c.qr_code, t.tipo, t.valor, t.data
            FROM transacao t
            JOIN cliente c ON c.cliente_id = t.cliente_id
            ORDER BY t.data DESC
        """)
        transacoes = [
            {
                "transacao_id": row.transacao_id,
                "nome": row.nome,
                "qr_code": row.qr_code,
                "tipo": row.tipo,
                "valor": float(row.valor),
                "data": str(row.data)
            }
            for row in cursor.fetchall()
        ]
        return jsonify({"status": "ok", "transacoes": transacoes})
    except Exception as e:
        return jsonify({"status": "erro", "msg": str(e)}), 500
    finally:
        if conn: conn.close()


# ── DASHBOARD ─────────────────────────────────────────────────────────
@app.route("/stats", methods=["GET"])
def stats():
    conn = None
    try:
        conn = get_conn()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM cliente")
        total_clientes = cursor.fetchone()[0]

        cursor.execute("SELECT ISNULL(SUM(saldo_credito), 0) FROM cliente")
        total_creditos = float(cursor.fetchone()[0])

        cursor.execute("SELECT COUNT(*) FROM transacao")
        total_transacoes = cursor.fetchone()[0]

        cursor.execute("SELECT ISNULL(AVG(saldo_credito), 0) FROM cliente")
        media_saldo = float(cursor.fetchone()[0])

        cursor.execute("SELECT COUNT(*) FROM transacao WHERE CAST(data AS DATE) = CAST(GETDATE() AS DATE)")
        transacoes_hoje = cursor.fetchone()[0]

        cursor.execute("SELECT TOP 5 nome, saldo_credito FROM cliente ORDER BY saldo_credito DESC")
        top_saldo = [{"nome": r.nome, "saldo_credito": float(r.saldo_credito)} for r in cursor.fetchall()]

        cursor.execute("""
            SELECT TOP 10 c.nome, t.tipo, t.valor, t.data
            FROM transacao t
            JOIN cliente c ON c.cliente_id = t.cliente_id
            ORDER BY t.data DESC
        """)
        ultimas = [{"nome": r.nome, "tipo": r.tipo, "valor": float(r.valor), "data": str(r.data)} for r in cursor.fetchall()]

        return jsonify({
            "status": "ok",
            "total_clientes": total_clientes,
            "total_creditos": total_creditos,
            "total_transacoes": total_transacoes,
            "media_saldo": media_saldo,
            "transacoes_hoje": transacoes_hoje,
            "top_saldo": top_saldo,
            "ultimas_transacoes": ultimas
        })
    except Exception as e:
        return jsonify({"status": "erro", "msg": str(e)}), 500
    finally:
        if conn: conn.close()


# ── ATRAÇÕES ──────────────────────────────────────────────────────────
@app.route("/stats_atracoes", methods=["GET"])
def stats_atracoes():
    conn = None
    try:
        conn = get_conn()
        cursor = conn.cursor()

        atracoes_def = [
            {"nome": "Carrossel",      "valor": 5.00},
            {"nome": "Roda-Gigante",   "valor": 10.00},
            {"nome": "Montanha-Russa", "valor": 15.00},
            {"nome": "Queda Livre",    "valor": 20.00},
        ]

        atracoes = []
        for a in atracoes_def:
            cursor.execute(
                "SELECT COUNT(*), ISNULL(SUM(valor), 0) FROM transacao WHERE tipo='saida' AND valor = ?",
                (a["valor"],)
            )
            row = cursor.fetchone()
            atracoes.append({
                "nome": a["nome"],
                "usos": row[0],
                "faturamento": float(row[1])
            })

        return jsonify({"status": "ok", "atracoes": atracoes})
    except Exception as e:
        return jsonify({"status": "erro", "msg": str(e)}), 500
    finally:
        if conn: conn.close()


# ── CRÉDITO EM LOTE ───────────────────────────────────────────────────
@app.route("/credito_lote", methods=["POST"])
def credito_lote():
    data = request.get_json()
    valor = data.get("valor")
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
        cursor.execute("SELECT COUNT(*) FROM cliente")
        total = cursor.fetchone()[0]
        if total == 0:
            return jsonify({"status": "erro", "msg": "Nenhum cliente cadastrado."}), 400
        cursor.execute("UPDATE cliente SET saldo_credito = saldo_credito + ?", (valor,))
        cursor.execute("""
            INSERT INTO transacao (cliente_id, tipo, valor)
            SELECT cliente_id, 'entrada', ? FROM cliente
        """, (valor,))
        conn.commit()
        return jsonify({"status": "ok", "msg": f"R$ {valor:.2f} adicionados para {total} visitantes!"})
    except Exception as e:
        return jsonify({"status": "erro", "msg": str(e)}), 500
    finally:
        if conn: conn.close()


# ── START — deve ser sempre a última linha ────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=5000)