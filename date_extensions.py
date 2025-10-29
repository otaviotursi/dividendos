import pandas as pd
from datetime import timedelta, datetime

def get_feriados_nacionais(ano):
    """Retorna uma lista com as datas dos principais feriados nacionais do ano."""
    feriados = [
        f"{ano}-01-01",  # Ano Novo
        f"{ano}-04-21",  # Tiradentes
        f"{ano}-05-01",  # Dia do Trabalho
        f"{ano}-09-07",  # Independência
        f"{ano}-10-12",  # Nossa Senhora Aparecida
        f"{ano}-11-02",  # Finados
        f"{ano}-11-15",  # Proclamação da República
        f"{ano}-12-25",  # Natal
    ]
    return [pd.to_datetime(data).date() for data in feriados]

def ajustar_para_dia_util(data, mover_para_frente=True):
    """Ajusta uma data para o próximo (ou anterior) dia útil se cair em fim de semana ou feriado."""
    data_original = data
    
    # Pega feriados do ano da data e do ano seguinte/anterior
    ano = data.year
    feriados = get_feriados_nacionais(ano)
    if mover_para_frente:
        feriados.extend(get_feriados_nacionais(ano + 1))
    else:
        feriados.extend(get_feriados_nacionais(ano - 1))

    while data.weekday() >= 5 or data.date() in feriados:  # 5 = sábado, 6 = domingo
        data += timedelta(days=1 if mover_para_frente else -1)
    
    if data != data_original:
        print(f"Data ajustada de {data_original.strftime('%Y-%m-%d')} para {data.strftime('%Y-%m-%d')}")
    
    return data

def ajustar_periodos(start, end, days_before, days_after):
    """
    Ajusta as datas de início e fim considerando dias úteis e feriados.
    
    Args:
        start: Data inicial
        end: Data final
        days_before: Número de dias para ajuste antes da data ex
        days_after: Número de dias para ajuste depois da data ex
    
    Returns:
        Tupla com (data_inicio, data_inicio_ajustada, data_fim, data_fim_ajustada)
        Todas as datas são retornadas no formato 'YYYY-MM-DD'
    """
    start_dt = pd.to_datetime(start)
    end_dt = pd.to_datetime(end)

    # Guarda as datas originais
    start_day = start_dt.strftime('%Y-%m-%d')
    end_day = end_dt.strftime('%Y-%m-%d')

    # Aplica offsets
    start_next = start_dt - timedelta(days=days_before)
    end_next = end_dt + timedelta(days=days_after)

    # Ajusta para dias úteis considerando feriados:
    # - start_next: mover para dia útil anterior
    # - end_next: mover para dia útil seguinte
    start_next = ajustar_para_dia_util(start_next, mover_para_frente=False)
    end_next = ajustar_para_dia_util(end_next, mover_para_frente=True)

    # Formata para string final
    start_next = start_next.strftime('%Y-%m-%d')
    end_next = end_next.strftime('%Y-%m-%d')

    print(start_day, start_next, end_day, end_next)
    return start_day, start_next, end_day, end_next