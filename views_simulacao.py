from flask import request, jsonify
from extensions import db
from app import app
from models import HistoricoEquipamento
from views_logic import verificar_status
from flask_sqlalchemy import SQLAlchemy


# importar config antes de criar db
app.config.from_object('config')

db = SQLAlchemy(app)

@app.route('/api/prever', methods=['POST'])
def prever(): 
    data = request.get_json()

    campos_obrigatorios = []
    for campo in campos_obrigatorios:
        if campo not in data:
            return jsonify({'erro': f'O campo "{campo}" é obrigatorio.'}), 400
    
    dados = {
    'pressao_entrada_sensor_bar': float(data['pressao_entrada']),
    'pressao_saida_sensor_bar':  float(data['pressao_saida']),
    'temperatura_ambiente_C': float(data['temperatura_ambiente']),
    'umidade_pct':  float(data['umidade']),
    'vibracao_mm_s': float(data['vibracao']),
    'posicao_pistao': float(data['posicao_pistao']),
    'tempo_ciclo_ms': float(data['tempo_ciclo_ms'])
    }
    
    # Usa sua função de regra de negócio
    resultado = verificar_status(dados)

    # Salvar no banco
    status, problemas = verificar_status(dados)
    novo_registro = HistoricoEquipamento(
        pressaoEntrada=float(dados['pressao_entrada_sensor_bar']),
        pressaoSaida=float(dados['pressao_saida_sensor_bar']),
        temperaturaAmbiente=float(dados['temperatura_ambiente_C']),
        umidadeInterna=float(dados['umidade_pct']),
        vibracao=float(dados['vibracao_mm_s']),
        posicaoPistao=float(dados['posicao_pistao']),
        tempoCiclo=float(dados['tempo_ciclo_ms']),
        result=status
    )

    db.session.add(novo_registro)
    db.session.commit()

    return jsonify({'resultado': verificar_status(dados)})

    #Postman relatorio
@app.route("/historico", methods=["GET"])
def listar_historico():
    resultados = HistoricoEquipamento.query.limit(100).all()  # ORM SQLAlchemy
    # converte objetos para dicionário
    lista = []
    for r in resultados:
        lista.append({
            "id": r.id,
            "pressaoEntrada": r.pressaoEntrada,
            "pressaoSaida": r.pressaoSaida,
            "temperaturaAmbiente": r.temperaturaAmbiente,
            "umidadeInterna": r.umidadeInterna,
            "vibracao": r.vibracao,
            "posicaoPistao": r.posicaoPistao,
            "tempoCiclo": r.tempoCiclo,
            "result": r.result,
            "criacao": r.criacao
        })
    return jsonify(lista)