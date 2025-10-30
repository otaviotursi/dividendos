import pandas as pd
from date_extensions import parse_date

def schedule_trades(df_trades, allow_overlap=False):
    """
    Seleciona operações com base nas datas.
    
    Args:
        df_trades: DataFrame com as operações
        allow_overlap: Se True, permite sobreposição de datas. Se False, 
                      garante que uma operação só começa após o término da anterior.
    """
    selected = []
    last_sell_date = None

    for _, trade in df_trades.iterrows():
        try:
            data_compra = parse_date(trade["DataCompra"])
            print(f"[DEBUG] Processando trade: Ticker={trade['Ticker']}, DataCom={trade['DataCom']}, DataCompra={data_compra}, DataVenda={trade['DataVenda']}")
            
            # Se permite sobreposição, adiciona todas as operações
            # Se não permite, verifica se a data de compra é posterior à última venda
            if allow_overlap or last_sell_date is None or data_compra > last_sell_date:
                selected.append(trade)
                last_sell_date = parse_date(trade["DataVenda"])
                
                if allow_overlap:
                    print(f"[INFO] Trade adicionado (sobreposição permitida)")
                else:
                    print(f"[INFO] Trade adicionado (sem sobreposição)")
            else:
                print(f"[INFO] Trade ignorado: data de compra {data_compra.strftime('%d/%m/%Y')} sobrepõe com venda anterior em {last_sell_date.strftime('%d/%m/%Y')}")
        
        except Exception as e:
            print(f"[WARN] Erro ao processar datas do trade: {e}")
            continue
    
    result = pd.DataFrame(selected)
    
    # Formata as datas para exibição
    if not result.empty:
        for col in ["DataCom", "DataCompra", "DataVenda"]:
            try:
                result[col] = result[col].apply(parse_date)
            except Exception as e:
                print(f"[WARN] Erro ao formatar coluna {col}: {e}")
        
    return result
