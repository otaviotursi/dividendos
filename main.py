from data_fetcher import get_dividend_events
from analyzer import rank_best_trades
from scheduler import schedule_trades
from backtester import run_backtest
from plotter import plot_equity_curve
from file_utils import save_trades_to_csv

def main():
    # Parâmetros configuráveis
    min_dy = 0.7  # DY mínimo
    days_before = 5  # Dias antes da data ex para compra
    days_after = 3  # Dias depois da data ex para venda
    allow_overlap = False  # Se permite sobreposição de datas
    valor_investido = 1000  # Capital inicial para backtest

    print("=== Estratégia de Dividendos B3 ===")
    start = "2024-01-01"
    end = "2025-10-28"

    print("\n🔍 Buscando eventos de dividendos...")
    eventos = get_dividend_events(start, end, min_dy=min_dy)
    print(f"{len(eventos)} eventos encontrados.")

    print("\n📈 Simulando operações...")
    trades = rank_best_trades(eventos, days_before, days_after, valor_investido)
    print("trades", len(trades))
    # print(trades.head())

    print(f"\n🧮 Montando cronograma {'COM' if allow_overlap else 'SEM'} sobreposição...")
    agendados = schedule_trades(trades, allow_overlap)
    print("agendados", len(agendados))

    # Salva os trades agendados em CSV com nome personalizado
    output_file = save_trades_to_csv(agendados, min_dy, days_before, days_after, allow_overlap)
    if output_file:
        print(f"💾 Trades salvos em: {output_file}")

    print("\n💰 Rodando backtest...")
    capital_final, hist = run_backtest(agendados, valor_investido)
    print(f"Capital final: R$ {capital_final:.2f}")

    plot_equity_curve(hist)
    print("📊 Gráfico gerado.")

if __name__ == "__main__":
    main()
