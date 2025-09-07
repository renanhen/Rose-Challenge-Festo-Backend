from flask import request, jsonify
from app import app  # se sua app for criada aqui; ajuste o import conforme seu projeto
from extensions import db
from models import LeituraSinal  # crie esse Model; exemplo abaixo

@app.route("/api/opcua/readings", methods=["POST"])
def opcua_readings():
    data = request.get_json(silent=True) or {}
    readings = data.get("readings", [])
    if not readings:
        return jsonify({"ok": False, "error": "payload vazio"}), 400

    objs = []
    for r in readings:
        tag = (r.get("tag") or "").strip()
        node_id = r.get("node_id")
        value = 1 if str(r.get("value")).lower() in ("1","true","t","on") or r.get("value") is True else 0
        ts = r.get("ts")  # ISO 8601
        if not tag or not ts:
            return jsonify({"ok": False, "error": f"linha inválida: {r}"}), 400
        from datetime import datetime
        ts_coleta = datetime.fromisoformat(ts.replace("Z", "+00:00")).replace(tzinfo=None)
        objs.append(LeituraSinal(tag=tag, node_id=node_id, valor_bool=value, ts_coleta=ts_coleta, origem="node-red"))

    db.session.bulk_save_objects(objs)
    db.session.commit()
    return jsonify({"ok": True, "ingest_count": len(objs)}), 201
