import requests
import pandas as pd
from itertools import chain
from datetime import datetime, timedelta
import os
import json

import yfinance as yf

from date_extensions import ajustar_periodos

def get_dividend_events(start, end, indice="ibovespa", min_dy=0.7, stock_filter=None):
    """
    Busca eventos de dividendos direto do StatusInvest.
    Filtra apenas DY >= min_dy (%).
    Suporta o novo formato da API que retorna listas aninhadas em 'dateCom', 'datePayment' e 'provisioned'.
    
    Args:
        start (str): Data inicial (YYYY-MM-DD)
        end (str): Data final (YYYY-MM-DD)
        indice (str): Índice para filtrar (default: ibovespa)
        min_dy (float): Dividend Yield mínimo em % (default: 0.7)
        stock_filter (str): Código do ativo específico para filtrar (opcional)
    """
    # Converte datas para datetime para manipulação
    start_date = pd.to_datetime(start)
    end_date = pd.to_datetime(end)
    
    all_responses = []
    current_date = start_date
    
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
    
    # Formata as datas para a URL
    current_str = current_date.strftime("%Y-%m-%d")
    period_end_str = end_date.strftime("%Y-%m-%d")
    
    # Nome do arquivo de cache para este período
    cache_file = f'data_cache/dividend_events_{current_str}_{period_end_str}.json'
    
    # Verifica se já temos os dados em cache
    if os.path.exists(cache_file):
        print(f"[INFO] Usando dados em cache para: {current_str} -> {period_end_str}")
        with open(cache_file, 'r', encoding='utf-8') as f:
            response_data = json.load(f)
    else:
        # Faz a requisição para o período
        url = f"https://statusinvest.com.br/acao/getearnings?IndiceCode={indice}&Filter=&Start={current_str}&End={period_end_str}"
        
        print(f"[INFO] Buscando proventos no StatusInvest: {current_str} -> {period_end_str}")
        
        r = requests.get(url, headers=headers)
        
        if r.status_code != 200:
            print(f"[ERRO] StatusInvest retornou {r.status_code}")
            print(r.text[:300])
        
        try:
            response_data = r.json()
            
            # Salva a resposta completa no cache
            os.makedirs('data_cache', exist_ok=True)
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(response_data, f, ensure_ascii=False, indent=2)
                
            print(f"[INFO] Dados salvos em cache: {cache_file}")
            
        except Exception as e:
            print(f"[ERRO] Falha ao processar resposta: {e}")
            print(r.text[:300])
    
    all_responses.append(response_data)

    # Processa todas as respostas
    all_events = []
    for response in all_responses:
        if not isinstance(response, dict):
            print("[WARN] Formato inesperado da resposta da API")
            continue
            
        # Extrai eventos de todos os tipos (JCP, dividendos, etc)
        eventos_raw = list(chain(
            response.get('datePayment', []),
            response.get('dateCom', []),
            response.get('provisioned', [])
        ))
        
        # Filtra por ativo específico se solicitado
        if stock_filter:
            eventos_raw = [e for e in eventos_raw if e.get('code', '').upper() == stock_filter.upper()]
        
        # Filtra por DY mínimo
        def parse_dy(dy_str):
            try:
                if isinstance(dy_str, (int, float)):
                    return float(dy_str)
                return float(str(dy_str).replace(',', '.'))
            except (ValueError, TypeError):
                return 0.0
        
        eventos_raw = [e for e in eventos_raw if parse_dy(e.get('dy', 0)) >= min_dy]
        
        all_events.extend(eventos_raw)
    
    if len(all_events) == 0:
        print("[WARN] Nenhum evento encontrado para o período")
        return pd.DataFrame()
        
    # Converte para DataFrame
    df = pd.DataFrame(all_events)
    
    # Renomeia colunas para formato mais amigável
    colunas = {
        'code': 'Ativo',
        'value': 'Valor',
        'dy': 'DY',
        'dateCom': 'DataCom',
        'datePayment': 'DataPagamento',
        'dateApproval': 'DataAprovacao',
        'earningType': 'Tipo'
    }
    
    df = df.rename(columns=colunas)
    
    # Ordena por data ex (DataCom)
    df = df.sort_values('DataCom')
    
    return df
    

def get_price_history(ticker, start_day, start_next, end_day, end_next):
    """
    Busca histórico de preços via Yahoo Finance (yfinance) para as datas especificadas.
    Retorna apenas os dados das 11:00 para as datas exatas de início e fim.
    """
    print(f"[INFO] Baixando histórico de {ticker}...")
    try:
        
        # Converte as datas de referência para datetime
        start_dt = pd.to_datetime(start_next)
        end_dt = pd.to_datetime(end_next)
        # Baixa dados do dia inicial
        ticker_obj = yf.Ticker(ticker)
        print(f"[INFO] Baixando dados de {start_next} para {ticker}...")
        df_start = ticker_obj.history(start=start_next, end=(start_dt + timedelta(days=1)), interval="1h")
        
        # Baixa dados do dia final
        print(f"[INFO] Baixando dados de {end_next} para {ticker}...")
        df_end = ticker_obj.history(start=end_next, end=(end_dt + timedelta(days=1)), interval="1h")
        
        # Combina os resultados
        df = pd.concat([df_start, df_end])
        
        if df.empty:
            print(f"[WARN] Nenhum dado disponível para {ticker}.")
            return pd.DataFrame()
        
        # Converte o índice para datetime se necessário
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
            
        
        # Debug: Mostra as datas e horas disponíveis
        print(f"[DEBUG] Datas buscadas: start={start_dt.date()}, end={end_dt.date()}")
        print(f"[DEBUG] Horas disponíveis para {ticker}:")
        for idx in df.index:
            print(f"Data: {idx.date()}, Hora: {idx.hour}")

        # Filtra primeiro por data
        df_dates = df[
            (df.index.date == start_dt.date()) | 
            (df.index.date == end_dt.date())
        ]
        
        if len(df_dates) == 0:
            print(f"[WARN] Nenhum dado encontrado para as datas {start_dt.date()} ou {end_dt.date()}")
            return pd.DataFrame()

        # Depois filtra por hora
        df_filtered = df_dates[df_dates.index.hour == 11]
        
        if len(df_filtered) < 2:
            print(f"[WARN] Dados insuficientes às 11h. Encontrados: {len(df_filtered)} registros")
            print("Tentando horário mais próximo...")
            
            # Se não encontrou 11h, pega o horário mais próximo para cada data
            result_list = []
            for target_date in [start_dt.date(), end_dt.date()]:
                day_data = df_dates[df_dates.index.date == target_date]
                if not day_data.empty:
                    # Pega o horário mais próximo de 11h
                    hour_diff = abs(day_data.index.hour - 11)
                    closest_time = day_data.iloc[hour_diff.argmin()]
                    result_list.append(closest_time)
            
            if len(result_list) == 2:
                result = pd.DataFrame(result_list)
                result['Date'] = result.index.strftime('%Y-%m-%d')
                print(f"[INFO] Usando horários alternativos para {ticker}")
                return result[["Date", "Open", "Close"]].reset_index(drop=True)
            else:
                return pd.DataFrame()
        
        # Se encontrou dados às 11h, usa eles
        result = df_filtered.copy()
        result['Date'] = result.index.strftime('%Y-%m-%d')
        return result[["Date", "Open", "Close"]].reset_index(drop=True)
            
    except Exception as e:
        print(f"[ERRO] Falha ao acessar dados para {ticker}: {e}")
        return pd.DataFrame()
