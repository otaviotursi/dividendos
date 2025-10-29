import pandas as pd
import os

def save_trades_to_csv(df, min_dy, days_before, days_after, allow_overlap):
    """
    Salva os trades em um arquivo CSV com nome baseado nos parâmetros.
    
    Args:
        df: DataFrame com os trades
        min_dy: DY mínimo usado na filtragem
        days_before: Dias antes da data ex para compra
        days_after: Dias depois da data ex para venda
        allow_overlap: Se foi permitida sobreposição de datas
    """
    try:
        # Cria diretório se não existir
        os.makedirs('data_cache', exist_ok=True)
        
        # Gera nome do arquivo com os parâmetros
        overlap_str = "com_sobreposicao" if allow_overlap else "sem_sobreposicao"
        output_file = f"data_cache/trades_dy{min_dy}_diasAntes{days_before}_diasDepois{days_after}_{overlap_str}.csv"
        
        # Salva o DataFrame
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"[INFO] Dados salvos em: {output_file}")
        
        return output_file
        
    except Exception as e:
        print(f"[ERRO] Falha ao salvar arquivo CSV: {e}")
        return None