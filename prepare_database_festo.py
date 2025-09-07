from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import errorcode
from datetime import datetime

# >>> CONFIG AQUI <<<
MYSQL_HOST = "127.0.0.1"
MYSQL_USER = "root"
MYSQL_PASS = "r3n@N47943911"
DB_NAME    = "FestoChallenge"

app = Flask(__name__)
CORS(app)

def get_conn(db=None):
    return mysql.connector.connect(
        host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASS, database=db
    )

def ensure_db_and_tables():
    # cria DB
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} "
                    "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;")
        cur.close(); conn.close()
    except mysql.connector.Error as err:
        print("Erro criando DB:", err); raise

    # cria tabela
    conn = get_conn(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS LeituraSinal (
            id INT AUTO_INCREMENT PRIMARY KEY,
            tag VARCHAR(128) NOT NULL,
            node_id VARCHAR(512) NULL,
            valor_bool TINYINT(1) NOT NULL,
            ts_coleta DATETIME NOT NULL,
            origem VARCHAR(64) DEFAULT 'node-red',
            ts_ins TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_tag_ts (tag, ts_coleta)
        ) ENGINE=InnoDB
          DEFAULT CHARSET=utf8mb4
          COLLATE=utf8mb4_bin;
    """)
    conn.commit()
    cur.close(); conn.close()

ensure_db_and_tables()

@app.route("/api/opcua/readings", methods=["POST"])
def ingest_readings():
    """
    Espera JSON assim:
    {
      "readings": [
        {"tag": "Avancado_1S2",
         "node_id": "ns=4;s=|var|CECC-LK.Application.IoConfig_Globals_Mapping.Avancado_1S2",
         "value": true,
         "ts": "2025-02-09T19:48:31Z",
         "origem": "node-red"}
      ]
    }
    """
    data = request.get_json(silent=True) or {}
    readings = data.get("readings", [])

    if not readings:
        return jsonify({"ok": False, "error": "payload vazio"}), 400

    rows = []
    for r in readings:
        tag = str(r.get("tag", "")).strip()
        node_id = r.get("node_id")
        val = r.get("value")
        ts = r.get("ts")  # ISO 8601
        origem = r.get("origem", "node-red")

        if tag == "" or ts is None or val is None:
            return jsonify({"ok": False, "error": f"linha inválida: {r}"}), 400

        # normaliza boolean (True/False/1/0/"true"/"false")
        vb = 1 if str(val).lower() in ("1", "true", "t", "on") or val is True else 0

        try:
            # aceita "Z" e sem timezone
            ts_coleta = datetime.fromisoformat(ts.replace("Z", "+00:00")).replace(tzinfo=None)
        except Exception:
            return jsonify({"ok": False, "error": f"ts inválido: {ts}"}), 400

        rows.append((tag, node_id, vb, ts_coleta, origem))

    try:
        conn = get_conn(DB_NAME)
        cur = conn.cursor()
        cur.executemany("""
            INSERT INTO LeituraSinal (tag, node_id, valor_bool, ts_coleta, origem)
            VALUES (%s, %s, %s, %s, %s)
        """, rows)
        conn.commit()
        cur.close(); conn.close()
    except mysql.connector.Error as err:
        return jsonify({"ok": False, "error": str(err)}), 500

    return jsonify({"ok": True, "ingest_count": len(rows)}), 201

@app.route("/api/opcua/last/<tag>", methods=["GET"])
def last_by_tag(tag):
    """Último valor de uma tag."""
    try:
        conn = get_conn(DB_NAME); cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT tag, valor_bool, ts_coleta, ts_ins
            FROM LeituraSinal
            WHERE tag=%s
            ORDER BY ts_coleta DESC
            LIMIT 1
        """, (tag,))
        row = cur.fetchone()
        cur.close(); conn.close()
    except mysql.connector.Error as err:
        return jsonify({"ok": False, "error": str(err)}), 500
    if not row:
        return jsonify({"ok": True, "data": None}), 200
    return jsonify({"ok": True, "data": row}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
