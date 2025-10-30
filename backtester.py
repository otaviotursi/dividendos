def run_backtest(trades_df, verbose, capital):
    historico = []

    for _, trade in trades_df.iterrows():
        ticker = trade["Ticker"]
        ticker = trade["Ticker"]
        data_com =trade["DataCom"]
        retorno_dividendo =trade["RetornoDividendoTotal(R$)"]
        retorno_valorizacao_acao =trade["RetornoValorizacaoTotal(R$)"]
        retorno_total_reais =trade["Retorno(R$)"]
        capital += retorno_total_reais
        
        # print(f"[DEBUG] Trade {trade['Ticker']}: Retorno {retorno_percentual}% => R$ {retorno_monetario:.2f}, Novo Capital: R$ {capital:.2f}")
        historico.append({
            "DataCom": trade["DataCom"],
            "DataCompra": trade["DataCompra"],
            "DataVenda": trade["DataVenda"],
            "Ticker": trade["Ticker"],
            "PrecoCompra": trade["PrecoCompra"],
            "PrecoVenda": trade["PrecoVenda"],
            "RetornoValorizacaoTotal(%)": trade["RetornoValorizacaoTotal(%)"],
            "RetornoDividendoTotal(%)": trade["RetornoDividendoTotal(%)"],
            "RetornoTotal(%)": trade["Retorno(%)"],
            "RetornoR$": round( trade["RetornoValorizacaoTotal(R$)"], 2),
            "Capital": round(capital, 2)
        })
        if verbose:
            print(f"ticker {ticker} | data_com {data_com} | retorno dividendo: R${retorno_dividendo:.2f} | retorno preco: R${retorno_valorizacao_acao:.2f} | retorno dividendo + valorizacao: R${retorno_total_reais:.2f} | Capital final: R${capital:.2f}")
        

    return capital, historico
