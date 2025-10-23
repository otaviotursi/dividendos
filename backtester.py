def run_backtest(trades_df, capital_inicial=1000):
    capital = capital_inicial
    historico = []

    for _, trade in trades_df.iterrows():
        # Calcula o valor monetário do retorno baseado no capital atual
        retorno_percentual = trade["Retorno(%)"]
        retorno_monetario = (capital * retorno_percentual) / 100
        capital += retorno_monetario

        historico.append({
            "DataCom": trade["DataCom"],
            "DataCompra": trade["DataCompra"],
            "DataVenda": trade["DataVenda"],
            "Ticker": trade["Ticker"],
            "PrecoCompra": trade["PrecoCompra"],
            "PrecoVenda": trade["PrecoVenda"],
            "RetornoPreco(%)": trade["RetornoPreco(%)"],
            "RetornoDividendo(%)": trade["RetornoDividendo(%)"],
            "RetornoTotal(%)": trade["Retorno(%)"],
            "RetornoR$": round(retorno_monetario, 2),
            "Capital": round(capital, 2)
        })

    return capital, historico
