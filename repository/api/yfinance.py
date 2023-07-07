import yfinance as yf
import pandas as pd

class YFinanceAPI:
    def get_data_multiple_tickers(self, tickers):
        """
        Fetch ticker information using yfinance API for the given tickers.
        Returns a DataFrame with the ticker information.
        """
        if not tickers or not isinstance(tickers, list):
            raise ValueError("Tickers should be a non-empty list.")
        
        ticker_data = []
        for ticker in tickers:
            try:
                response = yf.Ticker(ticker)
                if not response:
                    print(f"No response received for ticker {ticker}, skipping...")
                    continue
                
                info = response.info
                if not info:
                    print(f"No info received for ticker {ticker}, skipping...")
                    continue
                isin = info.get('isin')
                currency = info.get('currency')
                ticker_data.append({'ISIN': isin, 'Ticker': ticker, 'Currency': currency})
            except Exception as e:
                print(f"Error fetching information for ticker {ticker}: {e}")
                pass

        if ticker_data:
            df = pd.DataFrame(ticker_data)
            return df
        else:
            print("No data received for any of the tickers, returning None.")
            return pd.DataFrame()
