import os
import requests
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

class MarketDBApi:

    # Local Machine API Configuration
    # MARKET_DB_TOKEN = os.getenv('MARKET_DB_TOKEN')

    # Streamlit Configuration
    MARKET_DB_TOKEN = st.secrets["market_db_api"]["market_db_token"]

    def __init__(self):
        self.url = 'https://market-server.ethan-ai.com/api/add-ticker/'
        self.headers = {
            "Authorization": f"Token {self.MARKET_DB_TOKEN}",
            "type": "application/json",
            "Content-Type": "application/json"
        }

    def add_tickers(self, symbol_list):
        errored_symbols = []
        for symbol in symbol_list:
            payload = {"symbol": symbol}
            try:
                response = requests.post(self.url, json=payload, headers=self.headers)
                response.raise_for_status()

            except requests.exceptions.HTTPError as http_err:
                if response.json() and "message" in response.json():
                    if response.json()["message"] != "Ticker already exists.":                
                        errored_symbols.append(symbol)
            except Exception as err:
                errored_symbols.append(symbol)
