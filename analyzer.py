# analyzer.py
import pandas as pd
from datetime import datetime, timedelta
from data_fetcher import get_price_history
from date_extensions import ajustar_periodos,parse_date

def rank_best_trades(eventos_df, days_before, days_after, valor_investido):
    """
    Recebe um DataFrame com os eventos e retorna um DataFrame com os melhores trades,
    calculando o retorno total (preço + dividendo).
    
    Args:
        eventos_df: DataFrame com eventos de dividendos
        days_before: Número de dias úteis antes da data ex para compra
        days_after: Número de dias úteis depois da data ex para venda
        valor_investido: Valor inicial para investimento
    """
    if eventos_df.empty:
        print("[WARN] Nenhum evento para processar.")
        return pd.DataFrame(columns=["Ticker", "DataCom", "DY", "PrecoCompra", "PrecoVenda", "RetornoValorizacaoTotal(%)", "RetornoDividendoTotal(%)", "Retorno(%)"])

    df = eventos_df.copy()

    if df.empty:
        print("[WARN] Nenhum evento encontrado com DY >= maior que o setado.")
        return pd.DataFrame(columns=["Ticker", "DataCom", "DY", "PrecoCompra", "PrecoVenda", "RetornoValorizacaoTotal(%)", "RetornoDividendoTotal(%)", "Retorno(%)"])
    
    # Calcula retornos baseados nos preços reais
    resultados = []
    # print(df.head())
    for _, evento in df.iterrows():
        # print(f"[DEBUG] Processando evento: {evento['Ativo']} - DataCom: {evento['DataCom']} | {evento}")
        ticker = evento["Ativo"] + ".SA"  # Adiciona sufixo do Yahoo Finance
        try:
            data_com = parse_date(evento["DataCom"])
        except Exception as e:
            print(f"[WARN] Erro ao processar data para {evento['Ativo']}: {e}")
            continue
            
        start_day, start_next, end_day, end_next = ajustar_periodos(data_com, data_com, days_before, days_after)

        # Busca preços
        precos = get_price_history(ticker, start_day, start_next, end_day, end_next)
        # print(f"[DEBUG] Preços obtidos para {ticker} de {start_day} a {end_next}: {precos}")
        
        if not precos.empty and len(precos) >= 2:
            # Pega os preços das 11h dos respectivos dias
            preco_compra = precos.iloc[0]["Open"]  # Preço às 11h do dia da compra
            preco_venda = precos.iloc[-1]["Open"]  # Preço às 11h do dia da venda
            
            try:
                
                if start_next is None or end_next is None:
                    continue
                
                # Calcula retornos percentuais
                retorno_preco_porcentagem = ((preco_venda - preco_compra) / preco_compra) * 100
                retorno_dividendo_porcentagem = parse_dy(evento["DY"])  # Converte para float
                retorno_total_porcentagem = parse_dy(retorno_preco_porcentagem + retorno_dividendo_porcentagem)  # Garante que é float
                
                # Calcula valores em reais (R$)
                retorno_preco = (preco_venda - preco_compra)
                retorno_preco_reais_total = valor_investido * (parse_dy(retorno_preco_porcentagem) / 100)
                retorno_dividendo_reais = parse_dy(evento["ValorDividendo"])  # Converte para float
                retorno_dividendo_reais_total = (valor_investido / parse_dy(preco_compra) ) * parse_dy(evento["ValorDividendo"])  # Converte para float
                retorno_total_reais = retorno_preco_reais_total + retorno_dividendo_reais_total
                valor_total = valor_investido + retorno_total_reais
                
                print(f"[DEBUG] Trade {evento['Ativo']}: Retorno {retorno_total_porcentagem}% => R$ {retorno_total_reais:.2f}")
                resultados.append({
                    "Ticker": evento["Ativo"],
                    "DataCom": evento["DataCom"],
                    "DataCompra": start_next,
                    "DataVenda": end_next,
                    "DY": parse_dy(evento["DY"]),
                    "ValorDividendo": parse_dy(evento["ValorDividendo"]),
                    "PrecoCompra": round(parse_dy(preco_compra), 2),
                    "PrecoVenda": round(parse_dy(preco_venda), 2),
                    "RetornoValorizacaoTotal(%)": round(parse_dy(retorno_preco_porcentagem), 2),
                    "RetornoValorizacaoTotal(R$)": round(retorno_preco_reais_total, 2),
                    "RetornoValorizacaoPorAcao(R$)": round(retorno_preco, 2),
                    "RetornoDividendoTotal(%)": round(parse_dy(retorno_dividendo_porcentagem), 2),
                    "RetornoDividendoTotal(R$)": round(retorno_dividendo_reais_total, 2),
                    "RetornoDividendoPorAcao(R$)": round(retorno_dividendo_reais, 2),
                    "Retorno(%)": round(parse_dy(retorno_total_porcentagem), 2),
                    "Retorno(R$)": round(retorno_total_reais, 2),
                    "ValorInvestido(R$)": round(valor_investido, 2),
                    "ValorTotal(R$)": round(valor_total, 2),
                    "Valor": parse_dy(evento.get("Valor", 0)),
                    "Tipo": evento.get("Tipo", ""),
                })
            except Exception as e:
                print(f"[WARN] Erro ao processar {evento['Ativo']}: {e}")
    
    df_resultado = pd.DataFrame(resultados)

    if df_resultado.empty:
        print("[WARN] Nenhum trade válido encontrado.")
        return pd.DataFrame(columns=["Ticker", "Data", "DY", "PrecoCompra", "PrecoVenda", "RetornoValorizacaoTotal(%)", "RetornoDividendoTotal(%)", "Retorno(%)"])

    # Converte todas as colunas numéricas para float
    colunas_numericas = ["DY", "PrecoCompra", "PrecoVenda", "RetornoValorizacaoTotal(%)", "RetornoDividendoTotal(%)", "Retorno(%)"]
    for coluna in colunas_numericas:
        df_resultado[coluna] = pd.to_numeric(df_resultado[coluna], errors='coerce')

    # Remove linhas com valores nulos
    df_resultado = df_resultado.dropna()
    return df_resultado
    # Ordena pelo retorno total decrescente
    # return df_resultado.sort_values(by="Retorno(%)", ascending=False).reset_index(drop=True)

# Filtra por DY mínimo
def parse_dy(dy_str):
    try:
        if isinstance(dy_str, (int, float)):
            return float(dy_str)
        return float(str(dy_str).replace(',', '.'))
    except (ValueError, TypeError):
        return 0.0
