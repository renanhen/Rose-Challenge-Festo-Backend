from flask import Flask, render_template, request
import joblib
import pandas as pd
import plotly.express as px
import plotly.io as pio

app = Flask(__name__)
modelo = joblib.load('modelo_xgboost.pkl')  # seu modelo treinado


@app.route('/', methods=['GET'])
def form():
    return render_template('form.html', dados_antigos=None, erro=None, resultado=None)

@app.route('/prever', methods=['POST'])
def prever():
    data = request.form
    erro = None

    campos_obrigatorios = [
        'pressao', 'pressao_piloto', 'temperatura',
        'tempo_acionamento', 'frequencia', 'vazao'
    ]
    for campo in campos_obrigatorios:
        if not data.get(campo):
            erro = f'O campo \"{campo}\" não pode estar vazio.'
            return render_template('form.html', erro=erro, dados_antigos=data)
    # Prepara os dados no formato esperado pelo modelo

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

    return render_template('form.html', resultado=predicao, dados_antigos=data, erro=None)



@app.route('/')
def graficos():
    # Carrega o DataFrame
    dados = pd.read_csv('df_total.csv')

    # Gráfico 1: histograma
    figura_histograma = px.histogram(dados, x="temperatura_ambiente_C", title="Distribuição de temperatura")
    html_histograma = pio.to_html(figura_histograma, full_html=False)

    # Gráfico 2: boxplot
    figura_boxplot = px.box(dados, y="temperatura_ambiente_C", x="falha", title="Faixa de temperatura por falha", color="falha")
    html_boxplot = pio.to_html(figura_boxplot, full_html=False)

    return render_template('graficos.html', grafico_histograma=html_histograma, grafico_boxplot=html_boxplot)


if __name__=='__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)