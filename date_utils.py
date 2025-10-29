import pandas as pd

def parse_date(date_str):
    """
    Tenta converter string de data para datetime suportando múltiplos formatos.
    
    Args:
        date_str: String contendo a data em formato brasileiro (dd/mm/yyyy),
                 americano (mm/dd/yyyy) ou outros formatos suportados pelo pandas.
    
    Returns:
        datetime: Data convertida para objeto datetime
    """
    try:
        # Tenta formato brasileiro
        return pd.to_datetime(date_str, format='%d/%m/%Y')
    except:
        try:
            # Tenta formato americano
            return pd.to_datetime(date_str, format='%m/%d/%Y')
        except:
            # Se ambos falharem, tenta formato mixed
            return pd.to_datetime(date_str, format='mixed')