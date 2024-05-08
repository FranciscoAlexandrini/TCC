import pandas as pd
import yfinance as yf
from datetime import date
import pandas_ta as ta

def analyze_stock(stock, start, end, window_size):
    # Download dos dados históricos da ação do Yahoo Finance
    data = yf.download(stock, start=start, end=end)
    
    # Verifica se os dados foram baixados corretamente
    if not data.empty:
        # Reseta o índice para tratar a data como uma coluna
        data.reset_index(inplace=True)
        # Converte a coluna de data para o formato de string 'AAAA-MM-DD'
        data['Date'] = data['Date'].dt.strftime('%Y-%m-%d')
        # Calcula a variação percentual diária do preço de fechamento ajustado
        data['Var Percentual'] = data['Adj Close'].pct_change() * 100
        # Calcula a média móvel e o desvio padrão das variações percentuais
        media_rolling = data['Var Percentual'].rolling(window=window_size).mean()
        desvio_padrao_rolling = data['Var Percentual'].rolling(window=window_size).std()
        # Calculando o RSI
        rsi = ta.rsi(data['Adj Close'], length=14)
        data['RSI'] = rsi
        # Define os níveis de desvio para extremos
        dsv_sup2 = media_rolling + (desvio_padrao_rolling * 3)
        dsv_inf2 = media_rolling - (desvio_padrao_rolling * 3)

        # Filtrar dados
        results = pd.DataFrame({
            'Date': data['Date'],
            'Preco de Fechamento': data['Adj Close'],
            'RSI': data['RSI'],
            'Desvio': [
                'extremo_sobrecompra' if (x > dsv_sup2[idx] and rsi[idx] > 70) else
                'extremo_sobrevenda' if (x < dsv_inf2[idx] and rsi[idx] < 30) else None
                for idx, x in enumerate(data['Var Percentual'])
            ],
            'Stock': stock
        })

        # Remove linhas onde não há eventos de desvio (Desvio é None)
        results = results.dropna(subset=['Desvio']).reset_index(drop=True)
        return results
    else:
        return pd.DataFrame()

# Definição de parâmetros iniciais
stocksymbols = ["PETR4.SA", 'VALE3.SA', 'ITUB4.SA', 'BBAS3.SA', 'BBDC3.SA']
startdate = date(2002, 1, 1)
end_date = date(2023, 12, 31)
window_size = 100

# Processamento de múltiplas ações
all_results = pd.DataFrame()
for stock in stocksymbols:
    stock_results = analyze_stock(stock, startdate, end_date, window_size)
    if not stock_results.empty:
        # Combina os resultados de todas as ações em um único DataFrame
        all_results = pd.concat([all_results, stock_results], ignore_index=True)

# Salva os resultados finais em um arquivo JSON
if not all_results.empty:
    all_results.to_json('filtered_direcionais_results.json', orient='records')
    print(all_results.head())
else:
    print("Nenhum dado foi encontrado para as condições especificadas.")

