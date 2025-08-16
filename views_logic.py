def verificar_status(data):
    limites = {
    "pressao_entrada_sensor_bar": (1,10),
    "pressao_saida_sensor_bar":(1,10),
    "temperatura_ambiente_C":(-20, 80),
    "umidade_pct":(0, 90),
    "vibracao_mm_s":(0, 7),
    "tempo_ciclo_ms": (50, 500)
    }
    problemas = []

    # Pressões
    if not (limites["pressao_entrada_sensor_bar"][0] <= data["pressao_entrada_sensor_bar"] <= limites["pressao_entrada_sensor_bar"][1]):
        problemas.append('Pressão de entrada fora do limite')
    if not (limites["pressao_saida_sensor_bar"][0] <= data["pressao_saida_sensor_bar"] <= limites["pressao_saida_sensor_bar"][1]):
        problemas.append('Pressão de saída fora do limite')

    # Temperatura
    if not (limites["temperatura_ambiente_C"][0] <= data["temperatura_ambiente_C"] <= limites["temperatura_ambiente_C"][1]):
        problemas.append('Temperatura fora do limite')

    # Umidade
    if data["umidade_pct"] > limites["umidade_pct"][1]:
        problemas.append('Umidade acima do permitido')

    # Vibração
    if data["vibracao_mm_s"] > 10:
        problemas.append('Vibração crítica')
    elif data["vibracao_mm_s"] > 7:
        problemas.append('Vibração em alerta')

    # Tempo de ciclo
    if not (limites["tempo_ciclo_ms"][0] <= data["tempo_ciclo_ms"] <= limites["tempo_ciclo_ms"][1]):
        problemas.append('Tempo de ciclo fora do limite')

    if any("critica" in p or "fora" in p or "umidade" in p for p in problemas):
        status = "FALHA"
    elif any("alerta" in p for p in problemas):
        status = "ALERTA"
    else:
        status = "OK"

    return status, problemas

