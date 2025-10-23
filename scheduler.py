import pandas as pd

def schedule_trades(df_trades):
    """Seleciona operações sem sobreposição de datas."""
    df_trades = df_trades.sort_values(by="DataCom")
    selected = []
    last_sell_date = None

    for _, trade in df_trades.iterrows():
        # Converte datas para datetime, lidando com diferentes formatos possíveis
        try:
            data_compra = pd.to_datetime(trade["DataCompra"])
            if last_sell_date is None or data_compra > last_sell_date:
                selected.append(trade)
                last_sell_date = pd.to_datetime(trade["DataVenda"])
        except Exception as e:
            print(f"[WARN] Erro ao processar datas do trade: {e}")
            continue
    
    result = pd.DataFrame(selected)
    
    # Formata as datas para exibição
    if not result.empty:
        for col in ["DataCom", "DataCompra", "DataVenda"]:
            try:
                # Primeiro converte para datetime (aceita vários formatos)
                datas = pd.to_datetime(result[col])
                # Depois formata para o padrão brasileiro
                result[col] = datas.dt.strftime("%d/%m/%Y %H:%M")
            except Exception as e:
                print(f"[WARN] Erro ao formatar coluna {col}: {e}")
    
    return result
