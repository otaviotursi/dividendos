import requests
import pandas as pd
from itertools import chain

def get_dividend_events(start, end, indice="ibovespa", min_dy=0.7):
    """
    Busca eventos de dividendos direto do StatusInvest.
    Filtra apenas DY >= min_dy (%).
    Suporta o novo formato da API que retorna listas aninhadas em 'dateCom', 'datePayment' e 'provisioned'.
    """
    url = f"https://statusinvest.com.br/acao/getearnings?IndiceCode={indice}&Filter=&Start={start}&End={end}"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://statusinvest.com.br/acoes/proventos/ibovespa",
        "X-Requested-With": "XMLHttpRequest",
    }

    print(f"[INFO] Buscando proventos no StatusInvest: {start} -> {end}")
    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        print(f"[ERRO] StatusInvest retornou {r.status_code}")
        print(r.text[:300])
        return pd.DataFrame()

    try:
        data = r.json()
    except Exception:
        print("[ERRO] Resposta não é JSON, possivelmente bloqueio Cloudflare:")
        print(r.text[:300])
        return pd.DataFrame()

    # Verifica se a resposta possui as listas de eventos
    if not isinstance(data, dict):
        print("[WARN] Formato inesperado da resposta da API")
        return pd.DataFrame()

    eventos_raw = list(chain(
        data.get("dateCom", []),
        data.get("datePayment", []),
        data.get("provisioned", [])
    ))

    if len(eventos_raw) == 0:
        print("[WARN] Nenhum evento encontrado.")
        return pd.DataFrame()

    # Extrai campos relevantes de cada evento
    eventos = []
    for e in eventos_raw:
        eventos.append({
            "companyname": e.get("companyname"),
            "code": e.get("code"),
            "typeEarnings": e.get("typeEarnings"),
            "dataCom": e.get("dateCom"),
            "paymentDate": e.get("paymentDividend"),
            "approvedondate": e.get("approvedondate"),
            "value": e.get("value"),
            "dy":  pd.to_numeric(str(e.get("dy", "0")).replace(",", "."), errors="coerce")
        })

    # Filtra DY
    eventos = [e for e in eventos if e["dy"] >= min_dy]

    if len(eventos) == 0:
        print(f"[WARN] Nenhuma oportunidade encontrada com DY >= {min_dy}%")
        return pd.DataFrame(columns=["companyname", "code", "typeEarnings", "paymentDate", "approvedondate", "value", "dy"])

    df = pd.DataFrame(eventos)
    df = df.reset_index(drop=True)

    print(f"[INFO] {len(df)} eventos encontrados com DY >= {min_dy}%")
    return df

def get_price_history(ticker, start, end):
    """
    Busca histórico de preços via Yahoo Finance (yfinance) com dados intraday.
    Retorna o preço mais próximo das 11:00.
    """
    import yfinance as yf
    from datetime import datetime, timedelta

    print(f"[INFO] Baixando histórico de {ticker}...")
    try:
        # Baixa dados com intervalo de 1 hora
        ticker_obj = yf.Ticker(ticker)
        df = ticker_obj.history(start=start, end=end, interval="1h")
        
        if df.empty:
            print(f"[WARN] Nenhum dado disponível para {ticker}.")
            return pd.DataFrame()
        
        # Converte o índice para datetime se necessário
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
            
        # Filtra apenas os dados das 11:00
        df['hour'] = df.index.hour
        df_11h = df[df['hour'] == 11]
        
        if not df_11h.empty:
            # Reseta o índice e mantém a coluna de data
            df_11h = df_11h.copy()
            df_11h['Date'] = df_11h.index
            result = df_11h[["Date", "Open", "Close"]].reset_index(drop=True)
            return result
        else:
            print(f"[WARN] Nenhum dado às 11:00 disponível para {ticker}.")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"[ERRO] Falha ao acessar dados para {ticker}: {e}")
        return pd.DataFrame()
