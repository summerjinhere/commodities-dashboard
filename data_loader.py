import yfinance as yf
import pandas as pd
import streamlit as st

# Ticker mapping
COMMODITIES = {
    'Energy': {
        'Crude Oil': 'CL=F',
        'Natural Gas': 'NG=F',
        'Heating Oil': 'HO=F',
        'RBOB Gasoline': 'RB=F'
    },
    'Metals': {
        'Gold': 'GC=F',
        'Silver': 'SI=F',
        'Copper': 'HG=F',
        'Platinum': 'PL=F',
        'Palladium': 'PA=F'
    },
    'Agriculture': {
        'Corn': 'ZC=F',
        'Soybeans': 'ZS=F',
        'Chicago Wheat': 'ZW=F',
        'Sugar': 'SB=F',
        'Coffee': 'KC=F',
        'Cocoa': 'CC=F',
        'Cotton': 'CT=F'
    },
    'Livestock': {
        'Live Cattle': 'LE=F',
        'Lean Hogs': 'HE=F'
    }
}

ALL_TICKERS = []
for category in COMMODITIES.values():
    ALL_TICKERS.extend(category.values())

@st.cache_data
def fetch_data(start_date, end_date):
    """
    Fetches adjusted close prices for all defined commodities.
    """
    try:
        data = yf.download(
            ALL_TICKERS, 
            start=start_date, 
            end=end_date, 
            group_by='ticker',
            progress=False
        )
        
        # Extract Adj Close or Close
        df_prices = pd.DataFrame()
        
        for ticker in ALL_TICKERS:
            # yfinance download structure varies
            try:
                if isinstance(data.columns, pd.MultiIndex):
                    # Check if 'Adj Close' exists, else 'Close'
                    if (ticker, 'Adj Close') in data.columns:
                        series = data[(ticker, 'Adj Close')]
                    elif (ticker, 'Close') in data.columns:
                        series = data[(ticker, 'Close')]
                    else:
                        print(f"No price data for {ticker}")
                        continue
                else:
                    # Single ticker or flat structure case (unlikely with list download but safe to handle)
                    if 'Adj Close' in data.columns:
                        series = data['Adj Close']
                    else:
                        series = data['Close']
                        
                df_prices[ticker] = series
            except KeyError:
                print(f"Key error processing {ticker}")
                continue
                
        # Forward fill formatting gaps
        df_prices = df_prices.fillna(method='ffill')
        return df_prices

    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

def get_human_readable_name(ticker):
    for cat, items in COMMODITIES.items():
        for name, sym in items.items():
            if sym == ticker:
                return name
    return ticker
