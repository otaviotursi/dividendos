import pandas as pd
import itertools
import os
from datetime import datetime
from main import run_strategy

def generate_parameter_combinations():
    """Gera todas as combinações de parâmetros a serem testadas"""
    params = {
        'min_dy': [0.5, 0.7, 0.9, 1.1, 1.3, 1.5],
        'days_before': [1, 2, 3, 5, 7, 10, 12, 15, 20],
        'days_after': [1, 2, 3, 5, 7, 10, 12, 15, 20],
        'allow_overlap': [False, True],
        'valor_investido': [1000]  # Mantém fixo para comparação
    }
    
    # Gera todas as combinações possíveis
    keys = params.keys()
    combinations = [dict(zip(keys, v)) for v in itertools.product(*params.values())]
    
    return combinations

def init_results_file():
    """Inicializa o arquivo de resultados"""
    try:
        os.makedirs('optimization', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'optimization/results_{timestamp}.csv'
        
        # Cria arquivo com cabeçalho
        headers = ['min_dy', 'days_before', 'days_after', 'allow_overlap', 
                  'valor_investido', 'capital_final', 'retorno_percentual', 'csv_file']
        pd.DataFrame(columns=headers).to_csv(filename, index=False)
        
        return filename
    except Exception as e:
        print(f"[ERRO] Falha ao criar arquivo de resultados: {e}")
        return None

def save_result(filename, result):
    """Salva um único resultado no arquivo CSV"""
    try:
        # Lê resultados existentes
        df = pd.read_csv(filename)
        
        # Adiciona novo resultado
        df_new = pd.concat([df, pd.DataFrame([result])], ignore_index=True)
        
        # Salva arquivo atualizado
        df_new.to_csv(filename, index=False)
        
        # Mostra status atual
        capital_final = result['capital_final']
        retorno = result['retorno_percentual']
        print(f"💾 Resultado salvo em {filename}")
        
        # A cada resultado, mostra o ranking atualizado
        print("\n🏆 Top 5 configurações até agora:")
        top_results = df_new.sort_values('capital_final', ascending=False).head()
        print(top_results.to_string())
        
    except Exception as e:
        print(f"[ERRO] Falha ao salvar resultado: {e}")
        return None

def run_optimization(start_date="2024-01-01", end_date="2025-10-28"):
    """
    Executa a otimização testando várias combinações de parâmetros
    e salva os resultados incrementalmente.
    """
    print("=== Otimização de Parâmetros ===")
    
    # Inicializa arquivo de resultados
    results_file = init_results_file()
    if not results_file:
        print("[ERRO] Não foi possível criar arquivo de resultados")
        return None
    
    # Gera combinações de parâmetros
    combinations = generate_parameter_combinations()
    total = len(combinations)
    print(f"\nTestando {total} combinações de parâmetros...")
    
    # Testa cada combinação
    for i, params in enumerate(combinations, 1):
        print(f"\nProgresso: {i}/{total} ({i/total*100:.1f}%)")
        print(f"Testando: {params}")
        
        try:
            # Executa a estratégia com os parâmetros
            capital_final, _, csv_file = run_strategy(
                **params,
                start=start_date,
                end=end_date,
                verbose=False
            )
            
            # Prepara resultado
            result = {
                **params,
                'capital_final': capital_final,
                'retorno_percentual': ((capital_final - params['valor_investido']) / params['valor_investido']) * 100,
                'csv_file': csv_file
            }
            
            # Salva resultado imediatamente
            save_result(results_file, result)
            
            print(f"Resultado: R$ {capital_final:.2f} ({result['retorno_percentual']:.1f}%)")
            
        except Exception as e:
            print(f"[ERRO] Falha ao testar combinação: {e}")
            continue  # Continua para próxima combinação mesmo se houver erro
    
    return results_file

if __name__ == "__main__":
    run_optimization()