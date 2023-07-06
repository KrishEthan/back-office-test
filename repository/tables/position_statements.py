class PositionStatements: 

    def __init__(self, conn):
        self.conn = conn
        self.cursor = conn.cursor()

    def get_unique_asset_classes(self):
        """
        Fetch and return distinct asset classes from the database.
        """
        self.cursor.execute("SELECT DISTINCT asset_class FROM position_statements")
        asset_classes = [row[0] for row in self.cursor.fetchall()]
        return asset_classes
    
    def get_unique_client_name(self):
        """
        Fetch and return distinct client names from the database.
        """
        self.cursor.execute("SELECT DISTINCT client_name FROM position_statements")
        client_names = [row[0] for row in self.cursor.fetchall()]
        return client_names
    
    def get_unique_custodian_name(self):
        """
        Fetch and return distinct custodian names from the database.
        """
        self.cursor.execute("SELECT DISTINCT custodian_name FROM position_statements")
        custodian_names = [row[0] for row in self.cursor.fetchall()]
        return custodian_names
    
    def get_records(self, date, asset_class, client_name, custodian_name):
        """
        Fetch and return security id and mtm_price based on the provided date, 
        asset class, client name, and custodian name from the database.
        """
        query = f"SELECT security_id, mtm_price, isin, ccy from position_statements WHERE statement_date = '{date}'"
        conditions = []

        if asset_class != "All":
            conditions.append(f"asset_class = '{asset_class}'")

        if client_name != "All":
            conditions.append(f"client_name = '{client_name}'")

        if custodian_name != "All":
            conditions.append(f"custodian_name = '{custodian_name}'")

        if conditions:
            query += " AND " + " AND ".join(conditions)

        self.cursor.execute(query)
        return self.cursor.fetchall()