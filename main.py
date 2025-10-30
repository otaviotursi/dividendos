from data_fetcher import get_dividend_events
from analyzer import rank_best_trades
from scheduler import schedule_trades
from backtester import run_backtest
from plotter import plot_equity_curve
from file_utils import save_trades_to_csv

def run_strategy(
    min_dy=1.5,          # DY mínimo
    days_before=20,       # Dias antes da data ex para compra
    days_after=20,        # Dias depois da data ex para venda
    allow_overlap=True, # Se permite sobreposição de datas
    valor_investido=1000,# Capital inicial para backtest
    start="2023-10-26", # Data inicial
    end="2025-10-28",   # Data final
    verbose=True        # Se deve imprimir mensagens de progresso
):
    """
    Executa a estratégia de dividendos com os parâmetros especificados.
    
    Returns:
        tuple: (capital_final, histórico, arquivo_csv)
    """
    if verbose:
        print("=== Estratégia de Dividendos B3 ===")
        print(f"Parâmetros:")
        print(f"- DY mínimo: {min_dy}%")
        print(f"- Dias antes: {days_before}")
        print(f"- Dias depois: {days_after}")
        print(f"- Overlap: {'Sim' if allow_overlap else 'Não'}")
        print(f"- Capital inicial: R$ {valor_investido:.2f}")
        print(f"- Período: {start} até {end}")

    if verbose:
        print("\n🔍 Buscando eventos de dividendos...")
    eventos = get_dividend_events(start, end, min_dy=min_dy)
    # eventos = get_dividend_events(start, end, min_dy=min_dy, stock_filter="TOTS3")
    if verbose:
        print(f"{len(eventos)} eventos encontrados.")

    if verbose:
        print("\n📈 Simulando operações...")
    trades = rank_best_trades(eventos, days_before, days_after, valor_investido)
    if verbose:
        print(f"Trades gerados: {len(trades)}")

    if verbose:
        print(f"\n🧮 Montando cronograma {'COM' if allow_overlap else 'SEM'} sobreposição...")
    agendados = schedule_trades(trades, allow_overlap)
    if verbose:
        print(f"Trades agendados: {len(agendados)}")

    # Salva os trades agendados em CSV com nome personalizado
    output_file = save_trades_to_csv(agendados, min_dy, days_before, days_after, allow_overlap)
    if output_file and verbose:
        print(f"💾 Trades salvos em: {output_file}")

    if verbose:
        print("\n💰 Rodando backtest...")
    capital_final, hist = run_backtest(agendados, verbose, valor_investido)
    if verbose:
        print(f"Capital final: R$ {capital_final:.2f}")
        plot_equity_curve(hist)
        print("📊 Gráfico gerado.")
    
    return capital_final, hist, output_file

def main():
    """Executa a estratégia com os parâmetros padrão"""
    capital_final, hist, output_file = run_strategy()
    
if __name__ == "__main__":
    main()
