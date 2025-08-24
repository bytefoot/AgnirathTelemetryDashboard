import pandas as pd
import streamlit as st
import plotly.express as px
from geopy.distance import geodesic
import os

# Set the page title and layout
st.set_page_config(layout="wide")
st.title("Interactive Solar Vehicle Data Dashboard")

# Note: This script assumes a 'data.csv' file exists in the same directory.
# You will need to install the following libraries:
# pip install streamlit pandas plotly geopy

# 1. Read the data from a CSV file
try:
    # logpath = "/Users/kevinkinsey/Developer/Agnirath/HiddenValleyLogs/log_17aug_8"
    logpath = "/Users/kevinkinsey/Developer/Agnirath/d2/log"
    logfile = os.path.join(logpath, "output_data_A.csv")
    df = pd.read_csv(logfile)
except FileNotFoundError:
    st.error("Please ensure 'data.csv' is in the same directory as this script.")
    st.stop()

# 2. Perform data calculations
df['power_W'] = df['Bus_Voltage'] * df['Bus_Current']
df['net_solar_power_W'] = (df['Output_Voltage_A'] * df['Output_Current_A']) + \
                          (df['Output_Voltage_B'] * df['Output_Current_B']) + \
                          (df['Output_Voltage_C'] * df['Output_Current_C']) + \
                          (df['Output_Voltage_D'] * df['Output_Current_D'])

# 3. Calculate cumulative distance
df['distance_segment_km'] = 0.0
for i in range(1, len(df)):
    coords_1 = (df.loc[i-1, 'Latitude'], df.loc[i-1, 'Longitude'])
    coords_2 = (df.loc[i, 'Latitude'], df.loc[i, 'Longitude'])
    df.loc[i, 'distance_segment_km'] = geodesic(coords_1, coords_2).kilometers

df['cumulative_distance_km'] = df['distance_segment_km'].cumsum()
total_distance_km = df['distance_segment_km'].sum()

window_size = 5
df['rolling_power_W'] = df['power_W'].rolling(window=window_size).mean()

st.sidebar.markdown(f"**Total distance travelled:** {total_distance_km:.2f} km")

# 4. Create and display interactive plots using Plotly
st.header("Vehicle Velocity over Time")
fig_velocity = px.line(df, x='Timestamp', y='Vehicle_Velocity', title='Vehicle Velocity over Time')
st.plotly_chart(fig_velocity, use_container_width=True)

st.header("Power over Time (Raw vs. Rolling Average)")
# Create a new DataFrame for plotting to set custom colors
power_df = pd.DataFrame({
    'Timestamp': pd.concat([df['Timestamp'], df['Timestamp']], ignore_index=True),
    'Value': pd.concat([df['power_W'], df['rolling_power_W']], ignore_index=True),
    'Type': ['Raw Power'] * len(df) + ['Rolling Average'] * len(df)
})
power_df.loc[len(df):, 'Timestamp'] = df['Timestamp'].values
fig_power = px.line(power_df, x='Timestamp', y='Value', color='Type',
                    color_discrete_map={'Raw Power': 'blue', 'Rolling Average': 'orange'},
                    title=f'Power over Time with {window_size}-Point Rolling Average')
st.plotly_chart(fig_power, use_container_width=True)

st.header("Net Solar Power over Time")
fig_solar_power = px.line(df, x='Timestamp', y='net_solar_power_W', title='Net Solar Power over Time')
st.plotly_chart(fig_solar_power, use_container_width=True)

st.header("Velocity vs. Cumulative Distance")
fig_vel_vs_dist = px.line(df, x='cumulative_distance_km', y='Vehicle_Velocity', title='Velocity vs. Cumulative Distance')
st.plotly_chart(fig_vel_vs_dist, use_container_width=True)