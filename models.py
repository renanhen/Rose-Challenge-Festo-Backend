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
