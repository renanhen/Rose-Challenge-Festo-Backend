import mysql.connector
from flask import Flask, jsonify, request
from datetime import datetime
from flask_cors import CORS
from urllib.parse import unquote_plus

app = Flask(__name__)
# Habilita o CORS para permitir requisições do front-end React
CORS(app)

# Importa as configurações do seu arquivo config.py
from config import USUARIO, SENHA, SERVIDOR, DATABASE

# --- CONFIGURAÇÕES DO BANCO DE DADOS ---
# Lembre-se de substituir as credenciais abaixo pelas suas
# --- CONFIGURAÇÕES DO BANCO DE DADOS ---
DB_CONFIG = {
    'host': SERVIDOR,
    'user': USUARIO,
    'password': unquote_plus(SENHA),
    'database': DATABASE
}

def get_db_connection():
    """
    Função para criar uma conexão com o banco de dados MySQL.
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Erro de conexão com o banco de dados: {err}")
        return None

# --- FUNÇÃO DE BUSCA DO HISTÓRICO PARA O GRÁFICO ---
@app.route('/api/cylinder/history', methods=['GET'])
def get_cylinder_history():
    """
    Retorna os 20 pontos de histórico mais recentes para uma tag específica.
    """
    tag = request.args.get('tag')
    if not tag:
        return jsonify({"error": "Tag é necessária"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Falha na conexão com o banco de dados"}), 500

    cursor = conn.cursor(dictionary=True)
    
    # A consulta foi ajustada para ordenar os dados por timestamp de forma decrescente
    # e limitar a 20 registros, garantindo que o front-end sempre receba os mais recentes.
    query = "SELECT ts_ins AS ts, valor_bool AS valor FROM leiturasinal WHERE tag LIKE %s ORDER BY ts_ins DESC LIMIT 20"
    
    try:
        cursor.execute(query, (f'%{tag}%',))
        results = cursor.fetchall()
        
        # Formata o timestamp para o formato ISO 8601, que o JavaScript entende.
        for row in results:
            if isinstance(row['ts'], datetime):
                row['ts'] = row['ts'].isoformat()

        return jsonify(results)
    except mysql.connector.Error as err:
        print(f"Erro na execução da consulta: {err}")
        return jsonify({"error": "Erro ao buscar histórico"}), 500
    finally:
        cursor.close()
        conn.close()

# --- FUNÇÃO DE BUSCA DO STATUS MAIS RECENTE ---
def get_latest_readings_from_db():
    """
    Busca no banco de dados a leitura mais recente de cada tag, da tabela leiturasinal.
    Retorna um dicionário de tags e valores.
    """
    conn = None
    readings_dict = {}
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        tags_cilindro = ['Avancado_1S2', 'Recuado_1S1', 'Avancado_2S2', 'Recuado_2S1']
        for tag in tags_cilindro:
            query = """
            SELECT tag, valor_bool
            FROM leiturasinal
            WHERE tag = %s
            ORDER BY ts_ins DESC
            LIMIT 1;
            """
            cursor.execute(query, (tag,))
            result = cursor.fetchone()
            if result:
                readings_dict[result['tag']] = result['valor_bool']

    except mysql.connector.Error as err:
        print(f"Erro no banco de dados: {err}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
    
    return readings_dict

# --- ENDPOINT QUE SERVE OS DADOS PARA O FRONT-END REACT ---
@app.route('/api/cylinder/status', methods=['GET'])
def get_cylinder_status():
    """Busca o status mais recente dos cilindros no banco de dados e envia para o React."""
    
    dados_atuais = get_latest_readings_from_db()
    
    status_cilindro1 = "POSIÇÃO INDEFINIDA"
    if dados_atuais.get('Avancado_1S2') == 1:
        status_cilindro1 = "AVANÇADO"
    elif dados_atuais.get('Recuado_1S1') == 1:
        status_cilindro1 = "RECUADO"

    status_cilindro2 = "POSIÇÃO INDEFINIDA"
    if dados_atuais.get('Avancado_2S2') == 1:
        status_cilindro2 = "AVANÇADO"
    elif dados_atuais.get('Recuado_2S1') == 1:
        status_cilindro2 = "RECUADO"

    return jsonify({
        "statusCilindro1": status_cilindro1,
        "statusCilindro2": status_cilindro2
    })

# --- ENDPOINT QUE RECEBE DADOS DO NODE-RED ---
@app.route('/api/opcua/readings', methods=['POST'])
def process_readings():
    """Recebe dados do Node-RED e salva no banco de dados."""
    data = request.json
    readings = data.get('readings', [])
    
    salvar_no_mysql(readings)

    print("---------------------------------------")
    print("Status Atual dos Cilindros:")
    print("---------------------------------------")
    
    dados_atuais = {reading['tag']: reading['value'] for reading in readings}
    
    if dados_atuais.get('Avancado_1S2') is True:
        print("Cilindro 1: AVANÇADO")
    elif dados_atuais.get('Recuado_1S1') is True:
        print("Cilindro 1: RECUADO")
    else:
        print("Cilindro 1: POSIÇÃO INDEFINIDA")
    
    if dados_atuais.get('Avancado_2S2') is True:
        print("Cilindro 2: AVANÇADO")
    elif dados_atuais.get('Recuado_2S1') is True:
        print("Cilindro 2: RECUADO")
    else:
        print("Cilindro 2: POSIÇÃO INDEFINIDA")
    
    print("---------------------------------------")

    return jsonify({"ok": True, "ingest_count": len(readings)})

# --- FUNÇÃO DE SALVAMENTO NO BANCO DE DADOS ---
def salvar_no_mysql(readings):
    """Salva as leituras no banco de dados, na tabela leiturasinal."""
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Insere cada leitura na tabela 'leiturasinal', agora incluindo todas as colunas
        query = "INSERT INTO leiturasinal (tag, node_id, valor_bool, ts_coleta, origem, ts_ins) VALUES (%s, %s, %s, %s, %s, %s)"
        for reading in readings:
            # Converte o valor booleano para 0 ou 1
            valor_bool = 1 if reading['value'] else 0
            
            # Adiciona valores padrão para as colunas ausentes na requisição
            node_id_placeholder = "NODE_RED"  # Valor padrão
            origem_placeholder = "Node-RED"    # Valor padrão
            ts_coleta_agora = datetime.now()   # Usa a hora atual
            ts_ins_agora = datetime.now()      # Usa a hora atual

            cursor.execute(query, (reading['tag'], node_id_placeholder, valor_bool, ts_coleta_agora, origem_placeholder, ts_ins_agora))
        
        conn.commit()
        print("Dados salvos no banco de dados com sucesso.")
    
    except mysql.connector.Error as err:
        print(f"Erro ao salvar no banco de dados: {err}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    # Para rodar a aplicação, você deve instalar o Flask e o mysql-connector-python
    # pip install Flask mysql-connector-python
    app.run(debug=True, port=5000)
