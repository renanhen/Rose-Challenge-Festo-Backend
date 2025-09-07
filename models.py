from extensions import db
from datetime import datetime

class HistoricoEquipamento(db.Model):
    __tablename__ = 'historicoequipamento'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pressaoEntrada = db.Column(db.Float)
    pressaoSaida = db.Column(db.Float)
    temperaturaAmbiente = db.Column(db.Float)
    umidadeInterna = db.Column(db.Float)
    vibracao = db.Column(db.Float)
    posicaoPistao = db.Column(db.Float)
    tempoCiclo = db.Column(db.Float)
    result = db.Column(db.String(255), nullable=False)
    criacao = db.Column(db.DateTime, default=datetime.utcnow)

class LeituraSinal(db.Model):
    __tablename__ = "LeituraSinal"
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(128), nullable=False, index=True)
    node_id = db.Column(db.String(512))
    valor_bool = db.Column(db.Boolean, nullable=False)
    ts_coleta = db.Column(db.DateTime, nullable=False)
    origem = db.Column(db.String(64), default="node-red")