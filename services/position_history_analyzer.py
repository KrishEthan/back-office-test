import streamlit as st
from datetime import timedelta
import pandas as pd

class PositionHistoryAnalyzer:

    def __init__(self, position_history):
        self.position_history = position_history

    @staticmethod
    def calculate_percentage_change(current, previous):
        """
        This function calculates the percentage change between two values.
        """
        return round((current - previous) / previous * 100, 2) if previous != 0 else 0

    @staticmethod
    def prepare_table_data(significant_changes, previous_date_data, current_date_data, current_date, previous_date):
        """
        This function prepares data for the Streamlit table display.
        """
        table_data = []
        for security_id, difference in significant_changes:
            current_values = current_date_data[security_id]
            previous_values = previous_date_data.get(security_id, {"mtm_rpt_ccy": 0, "position_qty": 0, "mtm_price": 0})
            table_data.append({
                "Security ID": security_id,
                f"Position Quantity on {previous_date}": previous_values["position_qty"],
                f"MTM Price on {previous_date}": previous_values["mtm_price"],
                f"Local CCY {previous_date}": previous_values["mtm_rpt_ccy"],
                f"Position Quantity on {current_date}": current_values["position_qty"],
                f"MTM Price on {current_date}": current_values["mtm_price"],
                f"Local CCY {current_date}": current_values["mtm_rpt_ccy"],
                "Change (%)": difference
            })
        return table_data

    def run(self, current_date, asset_class, threshold):
        """
        This function runs the entire analysis and displays the results in Streamlit.
        """
        previous_date = current_date - timedelta(days=1)

        current_net_worth = self.position_history.get_net_worth(current_date, asset_class)
        previous_net_worth = self.position_history.get_net_worth(previous_date, asset_class)

        st.write(f"Networth on {previous_date} with asset class {asset_class} is {previous_net_worth}")
        st.write(f"Networth on {current_date} with asset class {asset_class} is {current_net_worth}")

        if previous_net_worth != 0:
            percentage_change = self.calculate_percentage_change(current_net_worth, previous_net_worth)
            st.write(f"Percentage change is {percentage_change}%")

            if abs(percentage_change) > threshold:
                st.markdown(f"<p style='color:red'>The difference is more than {threshold}%, it's {percentage_change}%.</p>", unsafe_allow_html=True)

                current_date_records = self.position_history.get_records(current_date, asset_class)
                previous_date_records = self.position_history.get_records(previous_date, asset_class)

                current_date_data = {record[0]: {"mtm_rpt_ccy": record[1], "position_qty": record[2], "mtm_price": record[3]} for record in current_date_records}
                previous_date_data = {record[0]: {"mtm_rpt_ccy": record[1], "position_qty": record[2], "mtm_price": record[3]} for record in previous_date_records}

                significant_changes = []
                for security_id, current_values in current_date_data.items():
                    previous_values = previous_date_data.get(security_id, {"mtm_rpt_ccy": 0, "position_qty": 0, "mtm_price": 0})
                    difference = self.calculate_percentage_change(current_values["mtm_rpt_ccy"], previous_values["mtm_rpt_ccy"])
                    if abs(difference) > threshold:
                        significant_changes.append((security_id, difference))

                if significant_changes:
                    st.write(f"Securities with more than {threshold}% changes:")
                    table_data = self.prepare_table_data(significant_changes, previous_date_data, current_date_data, current_date, previous_date)
                    st.dataframe(pd.DataFrame(table_data), use_container_width=True)
                else: 
                    st.write(f"No securities with more than {threshold}% changes.")
            else:
                st.markdown(f"<p style='color:green'>The difference is less than {threshold}%, it's {percentage_change}%.</p>", unsafe_allow_html=True)
        else:
            st.write("Unable to calculate the difference as the net worth for the previous date is zero.")
