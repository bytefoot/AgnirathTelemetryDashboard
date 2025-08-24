import streamlit as st
import pandas as pd
import os
from streamlit_autorefresh import st_autorefresh

# --- Configuration and File Path ---
st.set_page_config(layout="wide")
st.title("Interactive CSV Log Viewer 📊")
st.write("This viewer updates automatically every 2 seconds.")

logpath = "/Users/kevinkinsey/Developer/Agnirath/d2/log_aug22_track"
logpath = "/Users/kevinkinsey/Developer/Agnirath/d2/log"
logfile = os.path.join(logpath, "output_data_A.csv")
# logfile = "/Users/kevinkinsey/Developer/Agnirath/TrackTesting/afterlogs/output_data_A.csv"

# --- Set up the automatic refresh ---
# Refresh the app every 2000 milliseconds (2 seconds)
st_autorefresh(interval=1000, key="data-refresh")

# --- Main App Logic ---
if not os.path.exists(logfile):
    st.warning("Waiting for the log file to be created...")
else:
    try:
        # Read the CSV file directly, no need for caching herexxxxx
        df = pd.read_csv(logfile)

        # Sort the data by its index in reverse order
        df_sorted = df.sort_index(ascending=False)

        # Let the user choose which columns to display
        available_columns = df_sorted.columns.tolist()

        selected_columns = st.sidebar.multiselect(
            "Select columns to display:",
            options=available_columns,
            default=available_columns,
            key='column_selector_widget'
        )

        # Display the data in a table
        st.dataframe(df_sorted[selected_columns])

    except pd.errors.EmptyDataError:
        st.info("The CSV file is currently empty.")
    except Exception as e:
        st.error(f"An error occurred: {e}")