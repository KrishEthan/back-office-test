from utils.mapping import ticker_mapping
import streamlit as st
import pandas as pd
from repository.api.eodh import EodhAPI
from repository.api.open_figi import OpenFigiAPI
from repository.api.yfinance import YFinanceAPI


class PositionStatementAnalyzer:

    def __init__(self, position_statements, eod_prices):
        self.position_statements = position_statements
        self.eod_prices = eod_prices

    @staticmethod
    def calculate_percentage_change(mtm_price, close_price):
        """
        Calculate and return the percentage change between mtm_price and close_price.
        """
        return round((mtm_price - close_price) / close_price * 100, 2) if close_price != 0 else 0
    
    @staticmethod
    def santize_ticker(ticker_id):
        """
        Sanitize and return the ticker_id.
        """
        try:
            ticker_id_formatted = ticker_mapping.get(ticker_id, ticker_id)
            if ticker_id_formatted is None:
                return None
            if ticker_id_formatted not in ["BRK-B.US"]:
                ticker_id_formatted = ticker_id_formatted.replace('_', '.').replace('-', '.').replace(' ', '.')
            return ticker_id_formatted
        except Exception as e:
            raise ValueError(f"Error while sanitizing ticker: {str(e)}")
        
    @staticmethod
    def display_data(data, title, column_names):
        """
        Display data in the Streamlit app with given title and column names.
        """
        st.title(title)
        df = pd.DataFrame(data, columns=column_names)
        st.dataframe(df, use_container_width=True)
    
    def display_significant_changes(self, significant_changes):
        """
        Display significant changes in the Streamlit app.
        """
        st.title("Significant Changes")
        significant_df = pd.DataFrame(significant_changes, columns=["Security ID", "ISIN", "CCY", "MTM Price", "Close Price", "Difference"])
        st.dataframe(significant_df, use_container_width=True)

    def display_not_found_tickers(self, not_found_tickers):
        """
        Display not found tickers in the Streamlit app.
        """
        st.title("Not Found Tickers")
        not_found_df = pd.DataFrame(not_found_tickers, columns=["Security ID", "ISIN", "CCY", "MTM Price", "Close Price", "Difference"])
        st.dataframe(not_found_df, use_container_width=True)

    def display_security_found_eodh(self, security_found_eodh):
        """
        Display securities found in EODH in the Streamlit app.
        """
        st.title("Security Found in EODH")
        security_found_eodh_df = pd.DataFrame(security_found_eodh)
        st.dataframe(security_found_eodh_df, use_container_width=True)

    def display_securities_found_in_yfinance(self, yfinance_df):
        st.title("Securities Found in YFinance")
        st.dataframe(yfinance_df, use_container_width=True)

    
    def display_securities_not_found(self, securities_not_found):
        st.title("Securities Not Found in EODH and YFinance")
        st.dataframe(securities_not_found, use_container_width=True)


    def search_tickers_in_open_figi(self, not_found_tickers, open_figi_api):
        """
        Search tickers for not found tickers in OpenFigi API and return the merged DataFrame.
        """
        open_figi_df = pd.DataFrame()
        for ticker in not_found_tickers:
            isin = ticker[1]
            try:
                temp = open_figi_api.get_ticker_data(isin)
                open_figi_df = pd.concat([open_figi_df, temp], ignore_index=True)
            except Exception as e:
                raise ValueError(f"Error while searching tickers in OpenFigi API: {str(e)}")

        return open_figi_df
    
    def get_info_for_unique_tickers(self, merged_df, eodh_api):
        """
        Get ticker info for unique tickers using EodhAPI and return the results.
        """
        unique_tickers = merged_df['ticker'].unique().tolist()
        try:
            ticker_info = eodh_api.get_info_multiple_tickers(unique_tickers)
            return ticker_info
        except Exception as e:
            raise ValueError(f"Error while getting ticker info for unique tickers: {str(e)}")


    def add_security_code_column(self, not_found_tickers):
        """
        Add a 'Security Code' column to the not_found_tickers DataFrame.
        """
        not_found_df = pd.DataFrame(not_found_tickers, columns=["Security ID", "ISIN", "CCY", "MTM Price", "Close Price", "Difference"])
        not_found_df['Security Code'] = not_found_df['Security ID'].str.split('.').str[0]
        return not_found_df
    
    def find_security_in_eodh(self, ticker_info, not_found_df):
        """
        Find securities in EODH for not_found_df and return the results.
        """
        security_found_eodh = []
        for security_code in not_found_df["Security Code"]:
            if security_code in ticker_info['Code'].tolist():
                try:
                    currency = ticker_info.loc[ticker_info['Code'] == security_code, 'Currency'].iloc[0]
                    ccy = not_found_df.loc[not_found_df['Security Code'] == security_code, 'CCY'].iloc[0]
                    if currency == ccy:
                        security_found_eodh.append({"Security Code": security_code, "Currency": currency, "CCY": ccy})
                except Exception as e:
                    raise ValueError(f"Error while finding securities in EODH: {str(e)}")
        return security_found_eodh
    
    def get_not_found_tickers_eodh(self, not_found_df, security_found_eodh):
        security_codes = not_found_df['Security Code'].unique().tolist()

        for security in security_found_eodh:
            security_code = security['Security Code']
            if security_code in security_codes:
                security_codes.remove(security_code)

        return security_codes

    def get_securities_not_found(self, not_found_df, security_found_eodh, yfinance_df):
        if yfinance_df is not None:
            security_yfinance = yfinance_df['Ticker'].tolist()
        
            for security in security_found_eodh:
                security_yfinance.append(security['Security Code'])

            return not_found_df[~not_found_df['Security Code'].isin(security_yfinance)]
        else:
            return not_found_df
    


    def search_and_display_security_eodh(self, not_found_tickers):
        """
        Search and display securities found in EODH in the Streamlit app.
        """
        figi_api = OpenFigiAPI()
        eodh_api = EodhAPI()
        yfinance_api = YFinanceAPI()
        try:
            figi_tickers_df = self.search_tickers_in_open_figi(not_found_tickers, figi_api)
            
            ticker_info = self.get_info_for_unique_tickers(figi_tickers_df, eodh_api)
            ticker_info_df = pd.DataFrame(ticker_info)
            
            not_found_df = self.add_security_code_column(not_found_tickers)
            
            security_found_eodh = self.find_security_in_eodh(ticker_info_df, not_found_df)
            self.display_security_found_eodh(security_found_eodh)

            not_found_tickers_eodh = self.get_not_found_tickers_eodh(not_found_df, security_found_eodh)

            yfinance_df = yfinance_api.get_ticker_info(not_found_tickers_eodh)
            self.display_securities_found_in_yfinance(yfinance_df)

            securities_not_found = self.get_securities_not_found(not_found_df, security_found_eodh, yfinance_df)
            self.display_securities_not_found(securities_not_found)
        except ValueError as e:
            st.error(str(e))
            return


    def run(self, date, asset_class, client_name, custodian_name, threshold):
        """
        Run the analyzer and display the results using Streamlit.
        """
        position_records = self.position_statements.get_records(date, asset_class, client_name, custodian_name)
        
        significant_changes = []
        not_found_tickers = []
        for record in position_records:
            security_id = record[0]
            mtm_price = record[1]
            isin = record[2]
            ccy = record[3]
            security_id = self.santize_ticker(security_id)
            eod_price = self.eod_prices.get_records(date, security_id)
            
            if eod_price != 0:
                difference = self.calculate_percentage_change(mtm_price, eod_price)
                if abs(difference) >= threshold:
                    significant_changes.append((security_id, isin, ccy, mtm_price, eod_price, difference))
            else:
                not_found_tickers.append((security_id, isin, ccy, mtm_price, eod_price, 0))

    
        self.display_data(significant_changes, "Significant Changes", ["Security ID", "ISIN", "CCY", "MTM Price", "Close Price", "Difference"])
        self.display_data(not_found_tickers, "Not Found Tickers", ["Security ID", "ISIN", "CCY", "MTM Price", "Close Price", "Difference"])
        self.search_and_display_security_eodh(not_found_tickers)