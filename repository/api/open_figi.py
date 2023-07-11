import requests
import pandas as pd
from dotenv import load_dotenv
import os
import streamlit as st

class OpenFigiAPI:
    load_dotenv()

    # Local machine API Configuration
    # OPEN_FIGI_API_KEY = os.getenv("OPEN_FIGI_API_KEY")
    # OPEN_FIGI_BASE_URL = os.getenv("OPEN_FIGI_BASE_URL")
    # OPEN_FIGI_MAPPING_URL = OPEN_FIGI_BASE_URL + "/v3/mapping/"

    # Streamlit API Configuration
    OPEN_FIGI_BASE_URL = st.secrets["open_figi"]["base_url"]
    OPEN_FIGI_API_KEY = st.secrets["open_figi"]["api_key"]
    OPEN_FIGI_MAPPING_URL = OPEN_FIGI_BASE_URL + "/v3/mapping/"

    def __init__(self): 
        if not all([self.OPEN_FIGI_API_KEY, self.OPEN_FIGI_BASE_URL, self.OPEN_FIGI_MAPPING_URL]):
            raise ValueError("OpenFIGI API configurations are not fully set.")
        
        self.headers = {
            'Content-Type': 'text/json',
            'X-OPENFIGI-APIKEY': self.OPEN_FIGI_API_KEY,
        }

    def get_ticker_data(self, isin):
        if not isin:
            raise ValueError("ISIN is required.")
        
        data = [
            {"idType": "ID_ISIN", "idValue": isin},
        ]
        try:
            response = requests.post(self.OPEN_FIGI_MAPPING_URL, headers=self.headers, json=data)
            response.raise_for_status()  
            api_data = response.json()

            combined_data = []
            for item in api_data:
                combined_data.extend(item["data"])

            df = pd.DataFrame(combined_data)
            return df
        except Exception as error:
            raise error
