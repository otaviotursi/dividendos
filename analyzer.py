# analyzer.py
import pandas as pd
from datetime import datetime, timedelta
from data_fetcher import get_price_history

def rank_best_trades(eventos_df):
    """
    Recebe um DataFrame com os eventos e retorna um DataFrame com os melhores trades,
    filtrando DY >= 0.7 e calculando o retorno total (preço + dividendo).
    """
    if eventos_df.empty:
        print("[WARN] Nenhum evento para processar.")
        return pd.DataFrame(columns=["Ticker", "DataCom", "DY", "PrecoCompra", "PrecoVenda", "RetornoPreco(%)", "RetornoDividendo(%)", "Retorno(%)"])

    df = eventos_df.copy()

    if df.empty:
        print("[WARN] Nenhum evento encontrado com DY >= maior que o setado.")
        return pd.DataFrame(columns=["Ticker", "DataCom", "DY", "PrecoCompra", "PrecoVenda", "RetornoPreco(%)", "RetornoDividendo(%)", "Retorno(%)"])
    
    # Calcula retornos baseados nos preços reais
    resultados = []
    for _, evento in df.iterrows():
        ticker = evento["code"] + ".SA"  # Adiciona sufixo do Yahoo Finance
        try:
            # Converte a data considerando formato brasileiro
            data_com = pd.to_datetime(evento["dataCom"], format="%d/%m/%Y", dayfirst=True)
        except:
            try:
                # Tenta formato alternativo caso a data já esteja em outro formato
                data_com = pd.to_datetime(evento["dataCom"])
            except Exception as e:
                print(f"[WARN] Erro ao processar data para {evento['code']}: {e}")
                continue
        
        # Define datas D-1 e D+1
        data_compra = (data_com - timedelta(days=1)).strftime("%Y-%m-%d")
        data_venda = (data_com + timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Busca preços
        precos = get_price_history(ticker, data_compra, data_venda)
        
        if not precos.empty and len(precos) >= 2:
            preco_compra = precos.iloc[0]["Close"]  # Preço de fechamento D-1
            preco_venda = precos.iloc[-1]["Open"]   # Preço de abertura D+1
            
            try:
                # Pega as datas exatas dos preços
                data_compra_real = precos.iloc[0]["Date"] if not precos.empty else None
                data_venda_real = precos.iloc[-1]["Date"] if len(precos) > 1 else None
                
                if data_compra_real is None or data_venda_real is None:
                    continue
                
                # Calcula retorno percentual do trade
                retorno_preco = ((preco_venda - preco_compra) / preco_compra) * 100
                retorno_dividendo = float(evento["dy"])  # Converte para float
                retorno_total = float(retorno_preco + retorno_dividendo)  # Garante que é float
                
                resultados.append({
                    "Ticker": evento["code"],
                    "DataCom": evento["dataCom"],
                    "DataCompra": data_compra_real,
                    "DataVenda": data_venda_real,
                    "DY": float(evento["dy"]),
                    "PrecoCompra": round(float(preco_compra), 2),
                    "PrecoVenda": round(float(preco_venda), 2),
                    "RetornoPreco(%)": round(float(retorno_preco), 2),
                    "RetornoDividendo(%)": round(float(retorno_dividendo), 2),
                    "Retorno(%)": round(float(retorno_total), 2)
                })
            except Exception as e:
                print(f"[WARN] Erro ao processar {evento['code']}: {e}")
    
    df_resultado = pd.DataFrame(resultados)

    if df_resultado.empty:
        print("[WARN] Nenhum trade válido encontrado.")
        return pd.DataFrame(columns=["Ticker", "Data", "DY", "PrecoCompra", "PrecoVenda", "RetornoPreco(%)", "RetornoDividendo(%)", "Retorno(%)"])

    # Converte todas as colunas numéricas para float
    colunas_numericas = ["DY", "PrecoCompra", "PrecoVenda", "RetornoPreco(%)", "RetornoDividendo(%)", "Retorno(%)"]
    for coluna in colunas_numericas:
        df_resultado[coluna] = pd.to_numeric(df_resultado[coluna], errors='coerce')

    # Remove linhas com valores nulos
    df_resultado = df_resultado.dropna()

    # Ordena pelo retorno total decrescente
    return df_resultado.sort_values(by="Retorno(%)", ascending=False).reset_index(drop=True)
