class PositionHistory:

    def __init__(self, conn):
        self.conn = conn
        self.cursor = conn.cursor()

    def get_unique_asset_classes(self):
        """
        This function returns a list of distinct asset classes from the position history.
        """
        self.cursor.execute("SELECT DISTINCT asset_class FROM position_history")
        asset_classes = [row[0] for row in self.cursor.fetchall()]
        return asset_classes

    def get_net_worth(self, date, asset_class):
        """
        This function returns the net worth for a given date and asset class.
        """
        self.cursor.execute(f"SELECT SUM(mtm_rpt_ccy) FROM position_history WHERE report_date = '{date}' AND asset_class = '{asset_class}'")
        record = self.cursor.fetchone()
        return round(record[0], 4) if record[0] else 0

    def get_records(self, date, asset_class):
        """
        This function fetches the records from the position history for a given date and asset class.
        """
        self.cursor.execute(
            f"SELECT security_id, SUM(mtm_rpt_ccy), SUM(position_qty), SUM(mtm_price) FROM position_history WHERE report_date = '{date}' AND asset_class = '{asset_class}' GROUP BY security_id"
        )
        return self.cursor.fetchall()