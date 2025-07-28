from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd

app = Flask(__name__)
CORS(app)

modelo = joblib.load('modelo_xgboost.pkl')



@app.route('/api/prever', methods=['POST'])
def prever():
    data = request.get_json()  # recebe JSON do React

    # Validar dados (exemplo simples)
    campos_obrigatorios = ['pressao', 'pressao_piloto', 'temperatura', 'tempo_acionamento', 'frequencia', 'vazao', 'tipo_valvula', 'funcao_valvula', 'atuacao', 'conexao']
    for campo in campos_obrigatorios:
        if campo not in data:
            return jsonify({'erro': f'O campo "{campo}" é obrigatório.'}), 400
        
    dados = {
        'pressao_operacao_bar': float(data['pressao']),
        'pressao_piloto_bar': float(data['pressao_piloto']),
        'temperatura_ambiente_C': float(data['temperatura']),
        'tempo_acionamento_ms': float(data['tempo_acionamento']),
        'frequencia_comutacao_Hz': float(data['frequencia']),
        'vazao_l_min': float(data['vazao']),
        'piloto_interno': True,
        'bobina_festool': True,
        'ligacao_eletrica_ok': True,
        'manutencao_realizada': False,
        'tipo_valvula_MFH-3': int(data['tipo_valvula'] == 'MFH-3'),
        'tipo_valvula_MFH-5': int(data['tipo_valvula'] == 'MFH-5'),
        'tipo_valvula_MOFH-3': int(data['tipo_valvula'] == 'MOFH-3'),
        'tipo_valvula_VL/O-3': int(data['tipo_valvula'] == 'VL/O-3'),
        'funcao_valvula_5/2-way': int(data['funcao_valvula'] == '5/2-way'),
        'atuacao_Pneumática': int(data['atuacao'] == 'Pneumática'),
        'tamanho_conexao_G1/4': int(data['conexao'] == 'G1/4'),
        'tamanho_conexao_G1/8': int(data['conexao'] == 'G1/8'),
        'tamanho_conexao_G3/4': int(data['conexao'] == 'G3/4')
    }

    df = pd.DataFrame([dados])
    predicao = modelo.predict(df)[0]

    return jsonify({'resultado': int(predicao)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)