import yfinance as yf
import pandas as pd
import ta

def get_current_price(symbol):
    try:
        ticker = yf.Ticker(symbol)
        return ticker.fast_info['last_price']
    except Exception as e:
        print(f"Error fetching current price for {symbol}: {e}")
        return None

def get_historic_data(symbol, period="1d", interval="1m"):
    try:
        ticker = yf.Ticker(symbol)
        history = ticker.history(period=period, interval=interval)

        if history.empty:
            return pd.DataFrame()

        history['RSI']         = ta.momentum.rsi(history['Close'], window=7)
        history['SMA_5']       = ta.trend.sma_indicator(history['Close'], window=5)
        history['SMA_10']      = ta.trend.sma_indicator(history['Close'], window=10)

        macd = ta.trend.MACD(history['Close'], window_slow=13, window_fast=6, window_sign=5)
        history['MACD']        = macd.macd()
        history['MACD_SIGNAL'] = macd.macd_signal()
        history['MACD_DIFF']   = macd.macd_diff()

        bb = ta.volatility.BollingerBands(history['Close'], window=10, window_dev=2)
        history['BB_HIGH']     = bb.bollinger_hband()
        history['BB_LOW']      = bb.bollinger_lband()

        history = history.fillna(0)
        return history
    except Exception as e:
        print(f"Error fetching history for {symbol}: {e}")
        return pd.DataFrame()
