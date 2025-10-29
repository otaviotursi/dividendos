import pandas as pd
import itertools
import os
import time
from datetime import datetime, timedelta
from main import run_strategy


def generate_parameter_combinations():
    """Gera todas as combinações de parâmetros a serem testadas"""
    params = {
        'min_dy': [0.5, 0.7, 0.9, 1.1, 1.3, 1.5],
        'days_before': [1, 2, 3, 5, 7, 10, 12, 15, 20],
        'days_after': [1, 2, 3, 5, 7, 10, 12, 15, 20],
        'allow_overlap': [False, True],
        'valor_investido': [1000]
    }

    keys = params.keys()
    combinations = [dict(zip(keys, v)) for v in itertools.product(*params.values())]
    return combinations


def init_results_file():
    """Inicializa o arquivo de resultados"""
    try:
        os.makedirs('optimization', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'optimization/results_{timestamp}.csv'
        
        headers = [
            'min_dy', 'days_before', 'days_after', 'allow_overlap',
            'valor_investido', 'capital_final', 'retorno_percentual', 'csv_file'
        ]
        pd.DataFrame(columns=headers).to_csv(filename, index=False)
        return filename
    except Exception as e:
        print(f"[ERRO] Falha ao criar arquivo de resultados: {e}")
        return None


def save_result(filename, result):
    """Salva um único resultado no arquivo CSV"""
    try:
        df = pd.read_csv(filename)
        df_new = pd.concat([df, pd.DataFrame([result])], ignore_index=True)
        df_new.to_csv(filename, index=False)

        capital_final = result['capital_final']
        retorno = result['retorno_percentual']
        print(f"💾 Resultado salvo: R$ {capital_final:.2f} ({retorno:.2f}%)")

        top_results = df_new.sort_values('capital_final', ascending=False).head()
        print("\n🏆 Top 5 até agora:")
        print(top_results.to_string(index=False))
    except Exception as e:
        print(f"[ERRO] Falha ao salvar resultado: {e}")


def run_optimization(start_date="2024-01-01", end_date="2025-10-28"):
    """Executa a otimização testando várias combinações de parâmetros"""
    print("=== Otimização de Parâmetros ===")

    results_file = init_results_file()
    if not results_file:
        return None

    combinations = generate_parameter_combinations()
    total = len(combinations)
    print(f"\n🔢 Total de combinações: {total}")

    start_time = time.time()
    estimated_avg_time = None

    for i, params in enumerate(combinations, 1):
        print(f"\n➡️  Testando combinação {i}/{total} ({i / total * 100:.1f}%)")
        print(f"Parâmetros: {params}")

        try:
            iteration_start = time.time()

            capital_final, _, csv_file = run_strategy(
                **params,
                start=start_date,
                end=end_date,
                verbose=False
            )

            result = {
                **params,
                'capital_final': capital_final,
                'retorno_percentual': ((capital_final - params['valor_investido']) / params['valor_investido']) * 100,
                'csv_file': csv_file
            }
            save_result(results_file, result)

            iteration_time = time.time() - iteration_start

            # Atualiza tempo médio estimado
            if estimated_avg_time is None:
                estimated_avg_time = iteration_time
            else:
                estimated_avg_time = (estimated_avg_time * (i - 1) + iteration_time) / i

            # Calcula tempo restante
            elapsed = time.time() - start_time
            remaining = (total - i) * estimated_avg_time
            eta = datetime.now() + timedelta(seconds=remaining)

            print(f"⏱️ Tempo da iteração: {iteration_time:.2f}s | Média: {estimated_avg_time:.2f}s")
            print(f"⏳ Tempo total decorrido: {elapsed/60:.1f} min")
            print(f"🕒 Estimado restante: {remaining/60:.1f} min (termina ~{eta.strftime('%H:%M:%S')})")

        except Exception as e:
            print(f"[ERRO] Falha ao testar combinação: {e}")
            continue

    total_time = time.time() - start_time
    print(f"\n✅ Otimização concluída! Tempo total: {total_time/60:.1f} min")
    print(f"Resultados salvos em: {results_file}")
    return results_file


if __name__ == "__main__":
    run_optimization()
