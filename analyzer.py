# analyzer.py
import pandas as pd
from datetime import datetime, timedelta
from data_fetcher import get_price_history
from date_extensions import ajustar_periodos

def rank_best_trades(eventos_df,days_offset):
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
        ticker = evento["Ativo"] + ".SA"  # Adiciona sufixo do Yahoo Finance
        try:
            # Converte a data considerando formato brasileiro
            data_com = pd.to_datetime(evento["DataCom"], format="%d/%m/%Y", dayfirst=True)
        except Exception as e:
            try:
                # Tenta formato alternativo caso a data já esteja em outro formato
                data_com = pd.to_datetime(evento["DataCom"])
            except Exception as e:
                print(f"[WARN] Erro ao processar data para {evento['Ativo']}: {e}")
                continue
            
        start_day, start_next, end_day, end_next = ajustar_periodos(data_com, data_com, days_offset)

        # Busca preços
        precos = get_price_history(ticker, start_day, start_next, end_day, end_next)
        
        if not precos.empty and len(precos) >= 2:
            # Pega os preços das 11h dos respectivos dias
            preco_compra = precos.iloc[0]["Open"]  # Preço às 11h do dia da compra
            preco_venda = precos.iloc[-1]["Open"]  # Preço às 11h do dia da venda
            
            try:
                
                if start_next is None or end_next is None:
                    continue
                
                # Calcula retorno percentual do trade
                retorno_preco = ((preco_venda - preco_compra) / preco_compra) * 100
                retorno_dividendo = parse_dy(evento["DY"])  # Converte para float
                retorno_total = parse_dy(retorno_preco + retorno_dividendo)  # Garante que é float
                
                resultados.append({
                    "Ticker": evento["Ativo"],
                    "DataCom": evento["DataCom"],
                    "DataCompra": start_next,
                    "DataVenda": end_next,
                    "DY": parse_dy(evento["DY"]),
                    "PrecoCompra": round(parse_dy(preco_compra), 2),
                    "PrecoVenda": round(parse_dy(preco_venda), 2),
                    "RetornoPreco(%)": round(parse_dy(retorno_preco), 2),
                    "RetornoDividendo(%)": round(parse_dy(retorno_dividendo), 2),
                    "Retorno(%)": round(parse_dy(retorno_total), 2)
                })
            except Exception as e:
                print(f"[WARN] Erro ao processar {evento['Ativo']}: {e}")
    
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

# Filtra por DY mínimo
def parse_dy(dy_str):
    try:
        if isinstance(dy_str, (int, float)):
            return float(dy_str)
        return float(str(dy_str).replace(',', '.'))
    except (ValueError, TypeError):
        return 0.0
