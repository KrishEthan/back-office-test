class EodPrices:

    def __init__(self, conn):
        self.conn = conn
        self.cursor = conn.cursor()

    # Used to get ticker id and close from eod_prices table
    def get_records(self, date, security_id):
        """
        Fetch and return the close price for a given date and security id.
        If no record is found, return 0.
        """
        self.cursor.execute(
            f"SELECT ticker_id, close FROM eod_prices WHERE reporting_date = '{date}' AND ticker_id = '{security_id}'"
        )
        record = self.cursor.fetchone()
        return record[1] if record else 0
