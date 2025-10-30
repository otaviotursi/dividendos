import matplotlib.pyplot as plt
import pandas as pd

def plot_equity_curve(historico):
    df = pd.DataFrame(historico)
    
    # Cria figura com dois subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), height_ratios=[2, 1])
    
    # Plot superior: Evolução do capital
    ax1.plot(df["DataCom"], df["CapitalAcumulado(R$)"], marker="o", color="blue")
    ax1.set_title("Evolução do Capital - Estratégia de Dividendos")
    ax1.set_xlabel("Data")
    ax1.set_ylabel("Capital Acumulado(R$)")
    ax1.grid(True)
    
    # Plot inferior: Retornos por trade
    bar_width = 0.35
    x = range(len(df))
    
    ax2.bar(x, df["RetornoValorizacaoTotal(%)"], bar_width, label="Retorno Preço", color="orange")
    ax2.bar([i + bar_width for i in x], df["RetornoDividendoTotal(%)"], bar_width, label="Retorno Dividendo", color="green")
    
    ax2.set_title("Composição dos Retornos por Trade")
    ax2.set_xlabel("Trades")
    ax2.set_ylabel("Retorno (%)")
    ax2.set_xticks([i + bar_width/2 for i in x])
    ax2.set_xticklabels(df["Ticker"], rotation=45)
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    plt.show()
