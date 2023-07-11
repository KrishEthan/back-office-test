import os
import json
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
from database.database_connector import DatabaseConnector
from database.database_connector import StreamLitDatabaseConnector
from repository.tables.position_statements import PositionStatements
from services.asset_class_analyzer import AssetClassAnalyzer



def main():

    load_dotenv()
    
    # Local Machine Database Configurations

    # db_config = {
    #     "host": os.getenv("DB_HOST"),
    #     "port": os.getenv("DB_PORT"),
    #     "database": os.getenv("DB_DATABASE"),
    #     "user": os.getenv("DB_USER"),
    #     "password": os.getenv("DB_PASSWORD")
    # }

    # database = DatabaseConnector(db_config)
    # connection = database.connect()
    
    
    # Streamlit Share Database Configurations
    
    database = StreamLitDatabaseConnector()
    connection = database.connect(st.secrets.postgres)
    position_statements = PositionStatements(connection)
    asset_class_analyzer = AssetClassAnalyzer(position_statements)

    json_input = st.text_area("Enter JSON data:")
    if json_input:
        try:
            json_data_dict = eval(json_input)
            json_data_formatted_str = json.dumps(json_data_dict, indent=4)
            json_data = json.loads(json_data_formatted_str)
            if json_data.get("Table Name") == "Net Worth":
                selected_date = st.date_input("Select a date", datetime.now())
                if st.button("Submit"):
                    asset_class_analyzer.run(json_data, selected_date)
        except json.JSONDecodeError:
            st.error("Invalid JSON input.")

if __name__ == "__main__":
    if st.session_state.get('authenticated', False):
        main()
    else:
        st.warning('Please login to access this page') 