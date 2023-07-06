import os
from requests import Session
from dotenv import load_dotenv

class EodhAPI:
    load_dotenv()

    EODH_API_BASE_URL = os.getenv("EODH_API_BASE_URL")
    EODH_API_TOKEN = os.getenv("EODH_API_TOKEN")
    EODH_API_LIMIT = int(os.getenv("EODH_API_LIMIT"))

    def __init__(self):
        self.session = Session()
        self.session.params = {
            "fmt": "json",
            "api_token": self.EODH_API_TOKEN, 
            "limit": self.EODH_API_LIMIT,
        }
        self.session.headers.update({"Accept": "application/json"})
        
    def get_info(self, ticker):
        ticker = ticker.split(".")[0]
        url = f"{self.EODH_API_BASE_URL}/api/search/{ticker}"
        response = self.session.get(url)
        data = response.json()
        if response.status_code == 200:
            return data, data != []
        else:
            return data, False

    def get_info_multiple_tickers(self, tickers):
        results = []
        for ticker in tickers:
            data, success = self.get_info(ticker)
            if success:
                results.extend(data)
        return results

