# analyzer.py
import pandas as pd

def rank_best_trades(eventos_df):
    """
    Recebe um DataFrame com os eventos e retorna um DataFrame com os melhores trades,
    filtrando DY >= 0.7 e calculando um retorno fictício.
    """
    if eventos_df.empty:
        print("[WARN] Nenhum evento para processar.")
        return pd.DataFrame(columns=["Ticker", "Data", "DY", "Retorno(%)"])

    df = eventos_df.copy()

    if df.empty:
        print("[WARN] Nenhum evento encontrado com DY >= maior que o setado.")
        return pd.DataFrame(columns=["Ticker", "Data", "DY", "Retorno(%)"])

    # Calcula retorno fictício
    df["Retorno(%)"] = df["dy"]

    # Seleciona e renomeia colunas
    df = df.rename(columns={
        "code": "Ticker",
        "paymentDate": "Data",
        "dy": "DY"
    })[["Ticker", "Data", "DY", "Retorno(%)"]]

    # Ordena pelo retorno decrescente
    return df.sort_values(by="Retorno(%)", ascending=False).reset_index(drop=True)
