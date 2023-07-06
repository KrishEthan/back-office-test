import os
import streamlit as st
import psycopg2
from dotenv import load_dotenv
from database.database_connector import DatabaseConnector
from database.database_connector import StreamLitDatabaseConnector
from datetime import datetime
from repository.tables.position_statements import PositionStatements
from repository.tables.eod_prices import EodPrices
from services.position_statement_analyzer import PositionStatementAnalyzer


def main():
    st.set_page_config(layout="wide")

    load_dotenv()

    # Local Machine Database Configurations
    # 
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
    eod_prices = EodPrices(connection)
    position_statement_analyzer = PositionStatementAnalyzer(position_statements, eod_prices)

    st.title("Position Statement Analyzer")
    asset_classes = position_statements.get_unique_asset_classes()
    client_names = position_statements.get_unique_client_name()
    custodian_names = position_statements.get_unique_custodian_name()

    col1, col2, col3 = st.columns(3)
    with col1:
        asset_class = st.selectbox("Asset Class", ["All"] + asset_classes)
    with col2:
        client_name = st.selectbox("Client Name", ["All"] + client_names)
    with col3:
        custodian_name = st.selectbox("Custodian Name", ["All"] + custodian_names)


    col4, col5 = st.columns(2)
    with col4:
        threshold = st.number_input('Set a threshold percentage', min_value=1, max_value=10, value=5)
    with col5:
        selected_date = st.date_input("Select a date", datetime.now())

    if st.button("Submit"):
        position_statement_analyzer.run(selected_date, asset_class, client_name, custodian_name, threshold)
    
if __name__ == "__main__":
    main()  