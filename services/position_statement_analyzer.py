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


    def search_tickers_in_open_figi(self, missing_tickers, figi_api):
        """
        Search tickers for missing tickers in OpenFigi API and return the merged DataFrame.
        """
        if not missing_tickers:
            return pd.DataFrame()

        figi_tickers_df = pd.DataFrame()
        for ticker in missing_tickers:
            isin = ticker[1]
            try:
                temp_df = figi_api.get_ticker_data(isin)
                figi_tickers_df = pd.concat([figi_tickers_df, temp_df], ignore_index=True)
            except Exception as e:
                raise ValueError(f"Error while searching tickers in OpenFigi API: {str(e)}")

        return figi_tickers_df
    
    def get_info_for_unique_tickers(self, merged_df, eodh_api):
        """
        Get ticker info for unique tickers using EodhAPI and return the results.
        """
        if merged_df is not None and not merged_df.empty:
            unique_tickers = merged_df['ticker'].unique().tolist()

            if not unique_tickers:
                return pd.DataFrame()

            try:
                ticker_info = eodh_api.get_info_multiple_tickers(unique_tickers)
                ticker_info_df = pd.DataFrame(ticker_info)
                return ticker_info_df
            except Exception as e:
                raise ValueError(f"Error while getting ticker info for unique tickers: {str(e)}")
        else:
            return pd.DataFrame()

    def add_security_code_column(self, missing_tickers):
        """
        Add a 'Security Code' column to the missing_tickers DataFrame.
        """
        missing_tickers_df = pd.DataFrame(missing_tickers, columns=["Security ID", "ISIN", "Currency", "Mark To Market Price", "Close Price", "Difference"])
        missing_tickers_df['Security Code'] = missing_tickers_df['Security ID'].str.split('.').str[0]
        return missing_tickers_df
    
    def find_security_in_eodh(self, ticker_info_df, missing_tickers_df):
        """
        Find securities in EODH for missing_tickers_df and return the results.
        """
        if missing_tickers_df is None or missing_tickers_df.empty:
            return []
        
        securities_found_in_eodh = []
        for security_code in missing_tickers_df["Security Code"]:
            if security_code in ticker_info_df['Code'].tolist():
                try:
                    security_currency = ticker_info_df.loc[ticker_info_df['Code'] == security_code, 'Currency'].iloc[0]
                    record_currency = missing_tickers_df.loc[missing_tickers_df['Security Code'] == security_code, 'Currency'].iloc[0]
                    if security_currency == record_currency:
                        securities_found_in_eodh.append({"Security Code": security_code, "Currency": security_currency, "Record Currency": record_currency})
                except Exception as e:
                    raise ValueError(f"Error while finding securities in EODH: {str(e)}")
        return securities_found_in_eodh
    
    def get_missing_tickers_eodh(self, not_found_df, security_found_eodh):
        security_codes = not_found_df['Security Code'].unique().tolist()

        for security in security_found_eodh:
            security_code = security['Security Code']
            if security_code in security_codes:
                security_codes.remove(security_code)

        return security_codes

    def get_unfound_securities(self, missing_tickers_df, securities_found_in_eodh, yfinance_securities_df):
        yfinance_security_codes = yfinance_securities_df['Ticker'].tolist()

        for security in securities_found_in_eodh:
            yfinance_security_codes.append(security['Security Code'])

        return missing_tickers_df[~missing_tickers_df['Security Code'].isin(yfinance_security_codes)]


    def search_and_display_security_eodh(self, missing_tickers):
        """
        Search and display securities found in EODH in the Streamlit app.
        """
        if not missing_tickers:
            st.warning("No missing tickers to process.")
            return

        figi_api = OpenFigiAPI()
        eodh_api = EodhAPI()
        yfinance_api = YFinanceAPI()
        try:
            figi_tickers_df = self.search_tickers_in_open_figi(missing_tickers, figi_api)

            # Add 'Security Code' column to the missing_tickers DataFrame
            missing_tickers_df = self.add_security_code_column(missing_tickers)

            # Get ticker info for unique tickers
            ticker_info_df = self.get_info_for_unique_tickers(figi_tickers_df, eodh_api)

            # Find securities in EODH for missing_tickers_df
            securities_found_in_eodh = self.find_security_in_eodh(ticker_info_df, missing_tickers_df)
            
            # Display securities found in EODH
            self.display_security_found_eodh(securities_found_in_eodh)
            
            # Get remaining missing tickers after checking in EODH
            missing_tickers_eodh = self.get_missing_tickers_eodh(missing_tickers_df, securities_found_in_eodh)

            # Search for remaining missing tickers in YFinance
            yfinance_securities_df = yfinance_api.get_data_multiple_tickers(missing_tickers_eodh)
            
            # Display securities found in YFinance
            self.display_securities_found_in_yfinance(yfinance_securities_df)

            # Get unfound securities after searching in EODH and YFinance
            unfound_securities = self.get_unfound_securities(missing_tickers_df, securities_found_in_eodh, yfinance_securities_df)
            
            # Display unfound securities
            self.display_securities_not_found(unfound_securities)
            
        except Exception as e:
            st.error(f"Error occurred: {str(e)}")


    def run(self, date, asset_class, client_name, custodian_name, threshold):
        """
        Run the analyzer and display the results using Streamlit.
        """
        position_records = self.position_statements.get_records(date, asset_class, client_name, custodian_name)

        if not position_records:
            st.warning("No position records to process.")
            return
        
        significant_price_changes = []
        unidentified_tickers = []
        for record in position_records:
            security_id = record[0]
            market_to_market_price = record[1]
            isin = record[2]
            currency_code = record[3]
            sanitized_security_id = self.santize_ticker(security_id)
            eod_price = self.eod_prices.get_records(date, sanitized_security_id)

            if eod_price != 0:
                percentage_difference = self.calculate_percentage_change(market_to_market_price, eod_price)
                if abs(percentage_difference) >= threshold:
                    significant_price_changes.append((sanitized_security_id, isin, currency_code, market_to_market_price, eod_price, percentage_difference))
            else:
                unidentified_tickers.append((sanitized_security_id, isin, currency_code, market_to_market_price, eod_price, 0))


        self.display_data(significant_price_changes, "Significant Changes", ["Security ID", "ISIN", "CCY", "MTM Price", "Close Price", "Difference"])
        self.display_data(unidentified_tickers, "Not Found Tickers", ["Security ID", "ISIN", "CCY", "MTM Price", "Close Price", "Difference"])
        self.search_and_display_security_eodh(unidentified_tickers)