import os
import streamlit as st
from dotenv import load_dotenv
from database.database_connector import DatabaseConnector
from database.database_connector import StreamLitDatabaseConnector
from services.position_history_analyzer import PositionHistoryAnalyzer
from repository.tables.position_history import PositionHistory
from datetime import datetime


def main():
    st.set_page_config(layout="wide")

    load_dotenv()
    
    # Local Machine Database Configurations

    # db_config = {
    #     "host": os.getenv("DB_HOST"),
    #     "port": os.getenv("DB_PORT"),
    #     "database": os.getenv("DB_DATABASE"),
    #     "user": os.getenv("DB_USER"),
    #     "password": os.getenv("DB_PASSWORD")
    # }

    # database = DatabaseConnector(st.secrets.postgres)
    # connection = database.connect()
    
    
    # Streamlit Share Database Configurations
    
    database = StreamLitDatabaseConnector()
    connection = database.connect(st.secrets.postgres)
    position_history = PositionHistory(connection)
    position_history_analyzer = PositionHistoryAnalyzer(position_history)
    
    st.title("Position History Analyzer")
    asset_classes = position_history.get_unique_asset_classes()
    selected_asset_class = st.selectbox("Select an asset class", asset_classes)
    col1, col2 = st.columns(2)
    with col1:
        threshold = st.number_input('Set a threshold percentage', min_value=1, max_value=10, value=5)

    with col2:
        selected_date = st.date_input("Select a date", datetime.now())

    if st.button("Submit"):
        position_history_analyzer.run(selected_date, selected_asset_class, threshold)

if __name__ == "__main__":
    main()  