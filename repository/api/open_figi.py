import requests
import pandas as pd
from dotenv import load_dotenv
import os


class OpenFigiAPI:
    load_dotenv()

    OPEN_FIGI_API_KEY = os.getenv("OPEN_FIGI_API_KEY")
    OPEN_FIGI_BASE_URL = os.getenv("OPEN_FIGI_BASE_URL")
    OPEN_FIGI_MAPPING_URL = OPEN_FIGI_BASE_URL + "/v3/mapping/"

    def __init__(self):

        self.headers = {
            'Content-Type': 'text/json',
            'X-OPENFIGI-APIKEY': self.OPEN_FIGI_API_KEY,
        }

    def get_ticker_data(self, isin):
        data = [
            {"idType": "ID_ISIN", "idValue": isin},
        ]
        try:
            response = requests.post(self.OPEN_FIGI_MAPPING_URL, headers=self.headers, json=data)
            api_data = response.json()

            combined_data = []
            for item in api_data:
                combined_data.extend(item["data"])

            df = pd.DataFrame(combined_data)
            return df
        except Exception as error:
            print("OpenFigiAPI Error:", error)
