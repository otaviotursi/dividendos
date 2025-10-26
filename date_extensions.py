import pandas as pd
from datetime import timedelta

def ajustar_para_dia_util(data, mover_para_frente=True):
    """Ajusta uma data para o próximo (ou anterior) dia útil se cair em fim de semana."""
    while data.weekday() >= 5:  # 5 = sábado, 6 = domingo
        data += timedelta(days=1 if mover_para_frente else -1)
    return data

def ajustar_periodos(start, end, days_offset):
    start_dt = pd.to_datetime(start)
    end_dt = pd.to_datetime(end)

    start_day = start_dt.strftime('%Y-%m-%d')
    end_day = end_dt.strftime('%Y-%m-%d')

    # Aplica offsets
    start_next = start_dt - timedelta(days=days_offset)
    end_next = end_dt + timedelta(days=days_offset)

    # Se cair no fim de semana:
    # - start_next: mover para dia útil anterior (d-1)
    # - end_next: mover para dia útil seguinte (d+1)
    start_next = ajustar_para_dia_util(start_next, mover_para_frente=False)
    end_next = ajustar_para_dia_util(end_next, mover_para_frente=True)

    # Formata para string final
    start_next = start_next.strftime('%Y-%m-%d')
    end_next = end_next.strftime('%Y-%m-%d')

    print(start_day, start_next, end_day, end_next)
    return start_day, start_next, end_day, end_next