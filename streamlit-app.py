import streamlit as st
import requests
import pandas as pd
import plotly.graph_objs as go

API_KEY = st.secrets["api"]["alpha_vantage"]

def get_stock_data(symbol, outputsize="compact"):
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": "5min",
        "outputsize": outputsize,
        "apikey": API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "Time Series (5min)" not in data:
        st.error("❌ Error: Could not fetch data. Check the symbol or API limits.")
        return None

    df = pd.DataFrame.from_dict(data["Time Series (5min)"], orient="index", dtype=float)
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

def app():
    st.set_page_config(page_title="📊 AlphaVantage Stock Q&A", layout="wide")
    st.title("📊 Stock Dashboard (Alpha Vantage Only)")

    symbol = st.selectbox("Choose a stock symbol:", ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"])

    if symbol:
        df = get_stock_data(symbol)

        if df is not None:
            st.subheader(f"📈 {symbol} Candlestick Chart")
            fig = go.Figure(data=[go.Candlestick(
                x=df.index,
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"]
            )])
            fig.update_layout(title=f"{symbol} - Price Chart", xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("🔍 Data Overview")
            st.dataframe(df.tail())

            st.download_button("📥 Download CSV", df.to_csv(), file_name=f"{symbol}_data.csv")

            # GPT-related chat disabled:
            st.info("💡 GPT Q&A disabled due to quota limit. Re-enable once OpenAI API quota is available.")

if __name__ == "__main__":
    app()
