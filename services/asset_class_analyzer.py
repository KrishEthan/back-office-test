import pandas as pd
import streamlit as st
from utils.mapping import asset_map


class AssetClassAnalyzer:

    def __init__(self, position_statements):
        self.position_statements = position_statements

    def process_json(self, json_data):
        # Convert JSON data to pandas DataFrame
        df = pd.DataFrame(json_data["Data"])
        
        # Make the mapping case insensitive by converting all keys in asset_map to lower case
        asset_map_lower = {k.lower(): v for k, v in asset_map.items()}

        # Create a function to implement the mapping
        def map_type(value):
            if value is not None and '&' in value:
                asset_class = value.split('&')[0].strip().lower()  # Convert to lower case for case-insensitive comparison
                return asset_map_lower.get(asset_class, None)
            return None

        # Apply the function to the 'Type' column
        df['Type'] = df['Type'].apply(map_type)

        # Drop rows where 'Type' is None
        df.dropna(subset=['Type'], inplace=True)
        df.reset_index(inplace=True, drop=True)

        # Convert 'Total' column to numeric
        df['Total'] = df['Total'].str.replace(',', '').apply(pd.to_numeric, errors='coerce')

        # Calculate the total value
        total_value = df['Total'].sum()

        # Create a DataFrame for the total row
        total_df = pd.DataFrame({'Type': ['Total Value'], 'Total': [total_value]})

        # Concatenate the original DataFrame with the total row DataFrame
        df = pd.concat([df, total_df], ignore_index=True)
        df.rename(columns={'Type': 'Asset class'}, inplace=True)
        return df
    

    def run(self, json_data, date):

        df_processed = self.process_json(json_data)

        query_result = self.position_statements.get_asset_class_records(date)

        st.title("JSON Data")
        st.dataframe(df_processed, use_container_width=True)

        # Convert the query result to a DataFrame
        df_query = pd.DataFrame(query_result, columns=['Asset class', 'Total'])

        # Round the 'Value' column to 4 decimal places
        df_query['Total'] = df_query['Total'].round(4)

        st.title("Position Statement Data")
        st.dataframe(df_query, use_container_width=True)

        # Merge df_processed and df_query on 'Asset class'
        df_merged = pd.merge(df_processed, df_query, on='Asset class', how='outer', suffixes=('_processed', '_query'))

        # Calculate the percentage difference
        df_merged['Percentage Difference'] = ((df_merged['Total_processed'] - df_merged['Total_query']) / df_merged['Total_query']) * 100

        # Fill NaNs with 0
        df_merged.dropna(inplace=True)

        # Round 'Percentage Difference' to 2 decimal places
        df_merged['Percentage Difference'] = df_merged['Percentage Difference'].round(2)

        st.title("Difference between JSON and Position Statement")
        st.dataframe(df_merged, use_container_width=True)

