from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd


app = Flask(__name__)
CORS(app)

modelo = joblib.load('modelo_DSNU_xgboost.pkl')

@app.route('/api/prever', methods=['POST'])
def prever(): 
    data = request.get_json()

    campos_obrigatorios = []
    for campo in campos_obrigatorios:
        if campo not in data:
            return jsonify({'erro': f'O campo "{campo}" é obrigatorio.'}), 400
    
    dados = {
    'diametro_pistao_mm': float(data['diametro_pistao']),
    'clamping_unit': True,
    'horas_operacao': float(data['horas_operacao']),
    'manutencao_realizada': True,
    'curso_mm': float(data['curso_mm']),
    'temperatura_ambiente_C': float(data['temperatura_ambiente']),
    'pressao_operacao_bar': float(data['pressao_operacao_bar']),
    'velocidade_pistao_mm_s': float(data['velocidade_pistao']),
    'pressao_entrada_sensor_bar': float(data['pressao_entrada']),
    'pressao_saida_sensor_bar': float(data['pressao_saida']),
    'sensor_umidade_pct': float(data['sensor_umidade']),
    'vibracao_mm_s': float(data['vibracao']),
    'delta_pressao_bar': float(data['delta_pressao_bar']),
    'vazamento_detectado': False,
    'umidade_interna_detectada': float(data['umidade_interna']),
    'desgaste_detectado': True,
    'tipo_amortecimento_PPS': int(data['tipo_amortecimento'] == 'PPS'),
    'tipo_amortecimento_PPV': int(data['tipo_amortecimento'] == 'PPV'),
    'protecao_especial_Nenhuma': int(data['protecao_especial'] == 'Nenhuma'),
    'protecao_especial_R3': int(data['protecao_especial'] == 'R3'),
    'protecao_especial_R8': int(data['protecao_especial'] == 'R8'),
    'posicao_instalacao_Inclinada': int(data['posicao_instalacao'] == 'Inclinada'),
    'posicao_instalacao_Vertical': int(data['posicao_instalacao'] == 'Vertical')

}
    
    df = pd.DataFrame([dados])
    predicao = modelo.predict(df)[0]

    return jsonify({'resultado': int(predicao)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


['diametro_pistao_mm', 'clamping_unit', 'horas_operacao',
       'manutencao_realizada', 'curso_mm', 'temperatura_ambiente_C',
       'pressao_operacao_bar', 'velocidade_pistao_mm_s',
       'pressao_entrada_sensor_bar', 'pressao_saida_sensor_bar',
       'sensor_umidade_pct', 'vibracao_mm_s', 'delta_pressao_bar',
       'vazamento_detectado', 'umidade_interna_detectada',
       'desgaste_detectado', 'falha', 'tipo_amortecimento_PPS',
       'tipo_amortecimento_PPV', 'protecao_especial_Nenhuma',
       'protecao_especial_R3', 'protecao_especial_R8',
       'posicao_instalacao_Inclinada', 'posicao_instalacao_Vertical']