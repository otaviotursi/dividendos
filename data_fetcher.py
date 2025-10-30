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
            # response.get('datePayment', []),
            response.get('dateCom', [])
            # ,response.get('provisioned', [])
        ))

        # ajusta JCP para valor líquido (85%)
        for e in eventos_raw:
            tipo = e.get("earningType", "").upper()
            if tipo == "JCP":
                valor_bruto = float(str(e.get("resultAbsoluteValue", "0")).replace(",", "."))
                e["resultAbsoluteValue"] = round(valor_bruto * 0.85, 8)

        # remove o q é Rend. Tributado
        eventos_raw = [e for e in eventos_raw if e.get("earningType") != "Rend. Tributado"]

        # Filtra por ativo específico se solicitado
        if stock_filter:
            eventos_raw = [e for e in eventos_raw if e.get('code', '').upper() == stock_filter.upper()]
        
        # print(len(eventos_raw))
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
        
    # Converte para DataFrame e ordena por dateCom (mais antigo -> mais novo)
    df = pd.DataFrame(all_events)
    df['dateCom'] = pd.to_datetime(df['dateCom'], format='%d/%m/%Y', dayfirst=True)
    
    # Renomeia colunas para formato mais amigável
    colunas = {
        'code': 'Ativo',
        'value': 'Valor',
        'dy': 'DY',
        'resultAbsoluteValue': 'ValorDividendo',
        'dateCom': 'DataCom',
        'datePayment': 'DataPagamento',
        'dateApproval': 'DataAprovacao',
        'earningType': 'Tipo'
    }
    
    df = df.rename(columns=colunas)
    
    df = df.sort_values('DataCom', ascending=True)
    
    # Mostra os eventos ordenados
    print("\n[INFO] Eventos de dividendos encontrados:")
    for _, row in df.iterrows():
        print(f"{row['Ativo']}: {row['DataCom'].strftime('%d/%m/%Y')} - DY: {row['DY']}% - Tipo: {row['Tipo']}")
    
    # Converte DataCom de volta para string no formato original
    df['DataCom'] = df['DataCom'].dt.strftime('%d/%m/%Y')
    
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
        ticker_obj = yf.Ticker(ticker)

        # Nome dos arquivos de cache
        cache_start = f'data_cache/price_{ticker}_{start_next}.csv'
        cache_end = f'data_cache/price_{ticker}_{end_next}.csv'
        
        def process_dataframe(df):
            if not df.empty:
                # Converte índice para datetime se necessário
                if not isinstance(df.index, pd.DatetimeIndex):
                    df.index = pd.to_datetime(df.index)
                # Remove timezone info imediatamente
                df.index = df.index.tz_localize(None)
            return df

        # Tenta carregar dados iniciais do cache
        if os.path.exists(cache_start):
            print(f"[INFO] Usando dados em cache para {ticker} em {start_next}")
            df_start = pd.read_csv(cache_start, index_col=0, parse_dates=True)
            df_start = process_dataframe(df_start)
        else:
            print(f"[INFO] Baixando dados de {start_next} para {ticker}...")
            df_start = ticker_obj.history(start=start_next, end=(start_dt + timedelta(days=1)), interval="1h")
            df_start = process_dataframe(df_start)
            # Salva no cache (já com timezone removido)
            os.makedirs('data_cache', exist_ok=True)
            df_start.to_csv(cache_start)
            print(f"[INFO] Dados salvos em cache: {cache_start}")
        
        # Tenta carregar dados finais do cache
        if os.path.exists(cache_end):
            print(f"[INFO] Usando dados em cache para {ticker} em {end_next}")
            df_end = pd.read_csv(cache_end, index_col=0, parse_dates=True)
            df_end = process_dataframe(df_end)
        else:
            print(f"[INFO] Baixando dados de {end_next} para {ticker}...")
            df_end = ticker_obj.history(start=end_next, end=(end_dt + timedelta(days=1)), interval="1h")
            df_end = process_dataframe(df_end)
            # Salva no cache (já com timezone removido)
            os.makedirs('data_cache', exist_ok=True)
            df_end.to_csv(cache_end)
            print(f"[INFO] Dados salvos em cache: {cache_end}")
        
        # Verifica cada DataFrame individualmente
        if df_start.empty and df_end.empty:
            print(f"[WARN] Nenhum dado disponível para {ticker}.")
            return pd.DataFrame()
        elif df_start.empty:
            print(f"[INFO] Usando apenas dados do dia final para {ticker}")
            df = df_end
        elif df_end.empty:
            print(f"[INFO] Usando apenas dados do dia inicial para {ticker}")
            df = df_start
        else:
            # Se ambos têm dados, concatena
            df = pd.concat([df_start, df_end])
            
        if df.empty:
            print(f"[WARN] Nenhum dado disponível para {ticker} após processamento.")
            return pd.DataFrame()
        
        # Converte o índice para datetime UTC e depois para horário local
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        
        # Converte timezone-aware para timezone-naive removendo o fuso horário
        df.index = df.index.tz_localize(None)
            
        # Debug: Mostra as datas e horas disponíveis
        print(f"[DEBUG] Datas buscadas: start={start_dt.date()}, end={end_dt.date()}")

        # Filtra primeiro por data, convertendo para date para comparação
        df_dates = df[
            (df.index.date == start_dt.date()) | 
            (df.index.date == end_dt.date())
        ]
        
        if len(df_dates) == 0:
            print(f"[WARN] Nenhum dado encontrado para as datas {start_dt.date()} ou {end_dt.date()}")
            return pd.DataFrame()

        # print("result", df_dates)
        # Depois filtra por hora (11h no horário local)
        df_filtered = df_dates[df_dates.index.hour == 11]
        
        if len(df_filtered) < 2:
            print(f"[WARN] Dados insuficientes às 11h. Encontrados: {len(df_filtered)} registros")
            print("Tentando horário mais próximo...")
            
            # Se não encontrou 11h, pega o horário mais próximo para cada data
            result_list = []
            for target_date in [start_dt.date(), end_dt.date()]:
                day_data = df_dates[df_dates.index.date == target_date]
                if not day_data.empty:
                    # Remove timezone info se presente
                    day_data.index = day_data.index.tz_localize(None)
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
        print("[DEBUG] Detalhes do erro:")
        print(f"- Tipo do erro: {type(e).__name__}")
        print(f"- Datas requisitadas: {start_next} -> {end_next}")
        try:
            if 'df' in locals():
                print(f"- DataFrame possui dados: {'Sim' if not df.empty else 'Não'}")
                if not df.empty:
                    print(f"- Tipo do índice: {type(df.index)}")
                    print(f"- Timezone do índice: {df.index.tz if hasattr(df.index, 'tz') else 'None'}")
                    print("- Primeiros registros disponíveis:")
                    print(df.head())
        except Exception as debug_e:
            print(f"[WARN] Erro ao coletar informações de debug: {debug_e}")
        return pd.DataFrame()
