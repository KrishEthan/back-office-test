import yfinance as yf
import pandas as pd
import streamlit as st

class YFinanceAPI:
    def get_ticker_info(self, tickers):
        """
        Fetch ticker information using yfinance API for the given tickers.
        Returns a DataFrame with the ticker information.
        """
        ticker_data = []
        for ticker in tickers:
            print(f"Fetching information for ticker {ticker}")
            try:
                response = yf.Ticker(ticker)
                info = response.info
                isin = response.isin
                currency = info.get('currency')
                ticker_data.append({'ISIN': isin, 'Ticker': ticker, 'Currency': currency})
            except Exception as e:
                print(f"Error fetching information for ticker {ticker}: {e}")
                pass

        if ticker_data:
            df = pd.DataFrame(ticker_data)
            return df
        else:
            return None
