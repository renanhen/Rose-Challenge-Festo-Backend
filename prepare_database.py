import mysql.connector
from mysql.connector import errorcode

print("Conectando...")

try:
    conn = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='r3n@N47943911'
    )
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print('Existe algo errado no nome de usuário ou senha')
    else:
        print(err)
    exit()

cursor = conn.cursor()

cursor.execute("DROP database IF EXISTS FestoChallenge;")
cursor.execute("CREATE database FestoChallenge;")
cursor.execute("USE FestoChallenge;")

# Criação da tabela
TABLES = {}
TABLES['HistoricoEquipamento'] = ('''
    CREATE TABLE IF NOT EXISTS HistoricoEquipamento (
        id INT AUTO_INCREMENT PRIMARY KEY,
        pressaoEntrada DECIMAL(10,2),
        pressaoSaida DECIMAL(10,2),
        temperaturaAmbiente DECIMAL(10,2),                                                          
        umidadeInterna DECIMAL(10,2),
        vibracao DECIMAL(10,2),
        posicaoPistao DECIMAL(10,2),
        tempoCiclo DECIMAL(10,2),   
        result VARCHAR(255) NOT NULL,                                                           
        criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
''')

for tabela_nome in TABLES:
    tabela_sql = TABLES[tabela_nome]
    try:
        print(f"Criando tabela {tabela_nome}: ", end='')
        cursor.execute(tabela_sql)
        print("OK")
    except mysql.connector.Error as err:
        print(err.msg)

# Inserindo usuários
HistoricoEquipamento_sql = 'INSERT INTO HistoricoEquipamento ( pressaoEntrada, pressaoSaida, temperaturaAmbiente,umidadeInterna, vibracao, posicaoPistao, tempoCiclo, result) VALUES (%s, %s, %s, %s, %s, %s,%s, %s)'
HistoricoEquipamento = [
    (5.2, 4.9, 25.0, 40.0, 3.2, 50.0, 120, "OK"),
    (9.5, 9.2, 30.0, 35.0, 2.1, 60.0, 200, "OK"),
    (1.0, 1.2, 20.0, 45.0, 3.0, 40.0, 300, "OK"),
    (10.5, 9.8, 22.0, 38.0, 6.5, 55.0, 400, "FALHA"),  # pressão entrada fora
    (7.0, 11.5, 25.0, 50.0, 2.2, 45.0, 250, "FALHA"),  # pressão saída fora
    (6.0, 6.1, 90.0, 30.0, 4.0, 70.0, 200, "FALHA"),   # temperatura fora
    (8.0, 7.9, 15.0, 95.0, 3.1, 60.0, 100, "FALHA"),   # umidade fora
    (5.5, 5.2, 25.0, 50.0, 11.0, 65.0, 150, "FALHA"),  # vibração crítica
    (6.5, 6.0, 30.0, 40.0, 8.5, 50.0, 180, "ALERTA"),  # vibração em alerta
    (4.8, 5.0, -30.0, 20.0, 3.2, 40.0, 200, "FALHA"),  # temperatura abaixo
    (7.2, 6.9, 25.0, 60.0, 2.0, 55.0, 40, "FALHA"),    # tempo de ciclo fora
    (3.5, 3.2, 28.0, 30.0, 1.5, 42.0, 450, "OK"),
    (6.9, 7.0, 32.0, 80.0, 3.3, 65.0, 300, "OK"),
    (9.0, 8.8, 18.0, 85.0, 4.2, 48.0, 280, "ALERTA"),  # vibração em alerta
    (2.0, 1.8, 40.0, 60.0, 2.8, 50.0, 320, "OK"),
    (8.5, 8.1, 50.0, 70.0, 9.0, 55.0, 200, "ALERTA"),
    (6.2, 6.1, 25.0, 45.0, 2.5, 47.0, 480, "OK"),
    (7.8, 7.5, 19.0, 65.0, 3.8, 60.0, 350, "OK"),
    (10.2, 9.9, 10.0, 55.0, 2.7, 58.0, 100, "FALHA"),  # pressão entrada fora
    (4.2, 4.0, 27.0, 20.0, 7.5, 52.0, 300, "ALERTA")   # vibração alerta
]
cursor.executemany(HistoricoEquipamento_sql, HistoricoEquipamento)


conn.commit()
print('\n------------- HistoricoEquipamento -------------')
cursor.execute('SELECT * FROM HistoricoEquipamento')

# Consome os dados
for row in cursor.fetchall():
    print(row)

cursor.close()
conn.close()
print("\nBanco de dados HistoricoEquipamento criado com sucesso!")