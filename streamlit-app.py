import streamlit as st
import requests
import pandas as pd
import plotly.graph_objs as go

API_KEY = st.secrets["api"]["alpha_vantage"]

def get_stock_data(symbol, outputsize="full"):
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "outputsize": outputsize,
        "apikey": API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "Time Series (Daily)" not in data:
        st.error("❌ Error: Could not fetch data. Check the symbol or API limits.")
        return None

    df = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient="index", dtype=float)
    df.index = pd.to_datetime(df.index)
    df.rename(columns={
        "1. open": "Open",
        "2. high": "High",
        "3. low": "Low",
        "4. close": "Close",
        "5. volume": "Volume"
    }, inplace=True)
    df = df[["Open", "High", "Low", "Close", "Volume"]]
    df.sort_index(inplace=True)

    return df

def aggregate_data(df, freq):
    """Aggregate intraday data to daily, weekly, or monthly."""
    df_resampled = df.resample(freq).agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    })
    df_resampled.dropna(inplace=True)
    return df_resampled

def app():
    st.set_page_config(page_title="📊 AlphaVantage Stock Viewer", layout="wide")
    st.title("📊 Stock Dashboard with Timeframe Toggle")

    symbol = st.selectbox("Choose a stock symbol:", ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"])

    if symbol:
        df = get_stock_data(symbol)

        if df is not None:
            st.subheader(f"📈 {symbol} Candlestick Chart")
            view_option = st.radio("View timeframe:", ["Intraday", "Daily", "Weekly", "Monthly"], horizontal=True)

            if view_option == "Weekly":
                df_display = aggregate_data(df, "W")
            elif view_option == "Monthly":
                df_display = aggregate_data(df, "M")
            elif view_option == "Daily":
                df_display = aggregate_data(df, "D")
            else:
                df_display = df  # Intraday
            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=df_display.index,
                y=df_display["Close"],
                mode='lines',
                line=dict(color='royalblue', width=2),
                name='Close Price'
            ))

            fig.update_layout(
                title=f"{symbol} - Daily Price Chart",
                xaxis_rangeslider_visible=False,
                xaxis=dict(
                    rangeselector=dict(
                        buttons=list([
                            dict(count=7, label="1w", step="day", stepmode="backward"),
                            dict(count=30, label="1m", step="day", stepmode="backward"),
                            dict(count=90, label="3m", step="day", stepmode="backward"),
                            dict(count=180, label="6m", step="day", stepmode="backward"),
                            dict(step="all", label="All")
                        ])
                    ),
                    type="date"
                )
            )

            st.plotly_chart(fig, use_container_width=True)

            st.subheader("🔍 Data Overview")
            st.dataframe(df.tail())

            st.download_button("📥 Download CSV", df.to_csv(), file_name=f"{symbol}_daily_data.csv")

if __name__ == "__main__":
    app()
