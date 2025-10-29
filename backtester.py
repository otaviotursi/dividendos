def run_backtest(trades_df, capital_inicial):
    capital = capital_inicial
    historico = []

    for _, trade in trades_df.iterrows():
        # print(f"[DEBUG] Trade {trade['Ticker']}: Retorno {retorno_percentual}% => R$ {retorno_monetario:.2f}, Novo Capital: R$ {capital:.2f}")
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
            "RetornoR$": round( trade["RetornoPreco(R$)"], 2),
            "Capital": round( trade["Capital"], 2)
        })

    return capital, historico
