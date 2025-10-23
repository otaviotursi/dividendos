def run_backtest(trades_df, capital_inicial=1000):
    capital = capital_inicial
    historico = []

    for _, trade in trades_df.iterrows():
        capital += trade["Retorno(%)"]
        historico.append({
            "Data": trade["Data"],
            "Ticker": trade["Ticker"],
            "Capital": round(capital, 2)
        })

    return capital, historico
