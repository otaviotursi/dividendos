import pandas as pd

def schedule_trades(df_trades):
    """Seleciona operações sem sobreposição de datas."""
    df_trades = df_trades.sort_values(by="Data")
    selected = []
    last_sell_date = None

    for _, trade in df_trades.iterrows():
        if last_sell_date is None or trade["Data"] > last_sell_date:
            selected.append(trade)
            last_sell_date = trade["Data"]
    return pd.DataFrame(selected)
