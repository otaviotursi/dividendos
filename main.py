from data_fetcher import get_dividend_events
from analyzer import rank_best_trades
from scheduler import schedule_trades
from backtester import run_backtest
from plotter import plot_equity_curve

def main():
    print("=== Estratégia de Dividendos B3 ===")
    start = "2025-08-01"
    end = "2025-10-31"

    print("\n🔍 Buscando eventos de dividendos...")
    eventos = get_dividend_events(start, end, min_dy=0.7, stock_filter="SANB11")
    print(f"{len(eventos)} eventos encontrados.")

    print("\n📈 Simulando operações...")
    trades = rank_best_trades(eventos, 2)
    print(trades.head())

    print("\n🧮 Montando cronograma sem sobreposição...")
    agendados = schedule_trades(trades)
    print(agendados)

    print("\n💰 Rodando backtest...")
    capital_final, hist = run_backtest(agendados)
    print(f"Capital final: R$ {capital_final:.2f}")

    plot_equity_curve(hist)
    print("📊 Gráfico gerado.")

if __name__ == "__main__":
    main()
