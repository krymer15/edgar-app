# edgar-app/market_data.py

import yfinance as yf
from datetime import datetime

def get_stock_price_change_yf(symbol: str) -> str:
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d", interval="1m")

        if hist.empty:
            return "Real-time price data unavailable."

        latest_price = hist["Close"].iloc[-1]
        prev_close = ticker.info.get("previousClose", None)

        if not prev_close:
            return "Could not retrieve previous close."

        change_percent = ((latest_price - prev_close) / prev_close) * 100
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return (
            f"The stock is currently trading at ${latest_price:.2f} as of {timestamp}, "
            f"a change of {change_percent:.2f}% from the previous session’s close."
        )

    except Exception as e:
        return f"Real-time price lookup failed: {e}"

