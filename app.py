import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import data_loader

st.set_page_config(page_title="Commodities Momentum Dashboard", layout="wide")

# --- CSS Styling ---
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    .metric-card {
        background-color: #262730;
        border: 1px solid #464b5d;
        padding: 15px;
        border-radius: 5px;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

st.title("🚀 Commodities Momentum Dashboard")
st.markdown("Analyzing commodity price momentum across Energy, Metals, Agriculture, and Livestock sectors.")

# --- Sidebar Controls ---
st.sidebar.header("Configuration")

# Date Range
default_start = datetime(2015, 1, 1)
default_end = datetime(2025, 1, 31)

start_date = st.sidebar.date_input("Start Date", default_start)
end_date = st.sidebar.date_input("End Date", default_end)

# Momentum Lookback Windows
window_options = {
    '1 Month': 21,
    '3 Months': 63,
    '6 Months': 126,
    '12 Months': 252
}
selected_window_label = st.sidebar.selectbox("Momentum Window", list(window_options.keys()), index=3) # Default 12M
lookback_days = window_options[selected_window_label]

# --- Data Loading ---
with st.spinner('Fetching market data...'):
    df_prices = data_loader.fetch_data(start_date, end_date)

if df_prices.empty:
    st.error("No data fetched. Please check your internet connection or ticker symbols.")
    st.stop()

# --- Calculations ---
# Calculate rolling return (Momentum)
# Momentum = (Price_t / Price_{t-lookback}) - 1
df_momentum = df_prices.pct_change(periods=lookback_days)

# --- Visualization ---

# 1. Recent Momentum Snapshot
st.header(f"Snapshot: Current {selected_window_label} Momentum")
latest_date = df_momentum.index[-1]
st.info(f"Data as of: {latest_date.strftime('%Y-%m-%d')}")

# Get latest values, drop NaNs
latest_momentum = df_momentum.iloc[-1].dropna().sort_values(ascending=False)

# Map to readable names
readable_index = [data_loader.get_human_readable_name(t) for t in latest_momentum.index]
latest_momentum.index = readable_index

# Create Bar Chart
fig_bar = px.bar(
    latest_momentum, 
    x=latest_momentum.index, 
    y=latest_momentum.values,
    color=latest_momentum.values,
    color_continuous_scale='RdYlGn',
    labels={'y': 'Return', 'x': 'Commodity'},
    title=f"cross-sectional Momentum ({selected_window_label})"
)
fig_bar.update_layout(height=500, xaxis_tickangle=-45)
st.plotly_chart(fig_bar, use_container_width=True)

# 2. Historical Momentum Trends
st.header("Historical Momentum Trends")

# Multiselect for specific commodities to view
all_commodities_readable = [data_loader.get_human_readable_name(t) for t in df_prices.columns]
selected_commodities = st.multiselect(
    "Select Commodities to Compare:", 
    options=all_commodities_readable,
    default=all_commodities_readable[:5] # Default to first 5
)

# Filter data for plot
fig_line = go.Figure()

for readable_name in selected_commodities:
    # Reverse map readable name to ticker
    ticker = None
    for t in df_prices.columns:
        if data_loader.get_human_readable_name(t) == readable_name:
            ticker = t
            break
            
    if ticker and ticker in df_momentum.columns:
        fig_line.add_trace(go.Scatter(
            x=df_momentum.index,
            y=df_momentum[ticker],
            mode='lines',
            name=readable_name
        ))

fig_line.update_layout(
    title=f"Historical {selected_window_label} Momentum (Rolling Returns)",
    xaxis_title="Date",
    yaxis_title="Return",
    height=600,
    hovermode="x unified"
)
st.plotly_chart(fig_line, use_container_width=True)

# 3. Data Table
with st.expander("View Raw Data"):
    st.dataframe(df_prices.tail(100))
