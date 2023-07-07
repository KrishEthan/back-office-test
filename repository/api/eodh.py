import os
from requests import Session
from dotenv import load_dotenv
import streamlit as st

class EodhAPI:
    load_dotenv()
    
    # Local Machine API Configuration
    # EODH_API_BASE_URL = os.getenv("EODH_API_BASE_URL")
    # EODH_API_TOKEN = os.getenv("EODH_API_TOKEN")
    # EODH_API_LIMIT = int(os.getenv("EODH_API_LIMIT"))

    # Streamlit API Configuration
    EODH_API_BASE_URL = st.secrets["eodh_api"]["base_url"]
    EODH_API_TOKEN = st.secrets["eodh_api"]["api_token"]
    EODH_API_LIMIT = st.secrets["eodh_api"]["api_limit"]

    def __init__(self):
        if not all([self.EODH_API_BASE_URL, self.EODH_API_TOKEN, self.EODH_API_LIMIT]):
            raise ValueError("EOD API configurations are not fully set.")
        
        self.session = Session()
        self.session.params = {
            "fmt": "json",
            "api_token": self.EODH_API_TOKEN, 
            "limit": self.EODH_API_LIMIT,
        }
        self.session.headers.update({"Accept": "application/json"})
        
    def get_info(self, stock_ticker):
        ''' Fetches information for a given stock ticker. '''
        if not stock_ticker:
            raise ValueError("Stock ticker is required.")
        
        clean_ticker = stock_ticker.split(".")[0]
        request_url = f"{self.EODH_API_BASE_URL}/api/search/{clean_ticker}"

        try:
            response = self.session.get(request_url)
            response.raise_for_status()
            response_data = response.json()
            return response_data, response_data != []
        except Exception as error:
            print(f"EodhAPI: Error for {clean_ticker}",error)
            return [], False

    def get_info_multiple_tickers(self, stock_tickers):
        ''' Fetches information for multiple stock tickers. '''
        if not stock_tickers or not isinstance(stock_tickers, list):
            raise ValueError("Stock tickers should be a non-empty list.")
        combined_results = []
        for ticker in stock_tickers:
            ticker_data, fetch_successful = self.get_info(ticker)
            if fetch_successful and ticker_data:
                combined_results.extend(ticker_data)
        return combined_results

