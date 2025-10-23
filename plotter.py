import matplotlib.pyplot as plt
import pandas as pd

def plot_equity_curve(historico):
    df = pd.DataFrame(historico)
    plt.figure(figsize=(10, 5))
    plt.plot(df["Data"], df["Capital"], marker="o")
    plt.title("Evolução do Capital - Estratégia de Dividendos")
    plt.xlabel("Data")
    plt.ylabel("Capital (R$)")
    plt.grid()
    plt.show()
