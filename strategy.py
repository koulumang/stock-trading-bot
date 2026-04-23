import pandas as pd

STOP_LOSS_PCT   = 0.015   # exit if down 1.5%
TAKE_PROFIT_PCT = 0.03    # take profit at 3% gain
RSI_BUY         = 40      # more opportunities to buy
RSI_SELL        = 60      # quicker to sell on strength
MAX_POSITION_PCT = 0.25   # use up to 25% of portfolio per trade

def get_trade_decision(symbol, history_data, current_price, portfolio_context, currency='$'):
    try:
        if not isinstance(history_data, pd.DataFrame) or history_data.empty:
            return {"action": "HOLD", "quantity": 0, "reasoning": "No history data."}

        # Use last 3 candles for trend confirmation
        latest = history_data.iloc[-1]
        prev   = history_data.iloc[-2] if len(history_data) >= 2 else latest

        rsi       = latest.get('RSI', 50)
        macd_diff = latest.get('MACD_DIFF', 0)
        prev_macd = prev.get('MACD_DIFF', 0)
        bb_low    = latest.get('BB_LOW', 0)
        bb_high   = latest.get('BB_HIGH', 0)
        sma_5     = latest.get('SMA_5', current_price)
        sma_10    = latest.get('SMA_10', current_price)

        cash             = portfolio_context.get('cash', 0)
        total_value      = portfolio_context.get('total_value', cash)
        holdings_summary = portfolio_context.get('holdings_summary', [])

        current_qty = 0
        avg_price   = 0
        for h in holdings_summary:
            if h['symbol'] == symbol:
                current_qty = h['quantity']
                avg_price   = h['avg_price']
                break

        # --- Stop-loss / Take-profit ---
        if current_qty > 0 and avg_price > 0:
            pct = (current_price - avg_price) / avg_price
            if pct <= -STOP_LOSS_PCT:
                return {"action": "SELL", "quantity": current_qty,
                        "reasoning": f"Stop-loss hit ({pct*100:.2f}%)"}
            if pct >= TAKE_PROFIT_PCT:
                return {"action": "SELL", "quantity": current_qty,
                        "reasoning": f"Take-profit hit (+{pct*100:.2f}%)"}

        # --- Sell signal: RSI overbought OR MACD crossing down OR price near BB high ---
        macd_cross_down = macd_diff < 0 and prev_macd >= 0
        sell_signal = (
            rsi > RSI_SELL or
            macd_cross_down or
            (current_price >= bb_high * 0.995 and macd_diff < 0)
        )
        if current_qty > 0 and sell_signal:
            return {"action": "SELL", "quantity": current_qty,
                    "reasoning": f"Sell: RSI={rsi:.1f}, MACD_cross={macd_cross_down}"}

        # --- Buy signal: RSI oversold OR MACD crossing up OR price near BB low + uptrend ---
        macd_cross_up = macd_diff > 0 and prev_macd <= 0
        trend_up      = sma_5 > sma_10
        buy_signal = (
            (rsi < RSI_BUY and trend_up) or
            macd_cross_up or
            (current_price <= bb_low * 1.005 and macd_diff > 0)
        )
        if current_qty == 0 and buy_signal and cash > current_price:
            invest   = min(total_value * MAX_POSITION_PCT, cash * 0.95)
            quantity = int(invest // current_price)
            if quantity <= 0:
                return {"action": "HOLD", "quantity": 0, "reasoning": "Insufficient funds for one share"}
            return {"action": "BUY", "quantity": quantity,
                    "reasoning": f"Buy: RSI={rsi:.1f}, MACD_cross={macd_cross_up}, trend_up={trend_up}"}

        return {"action": "HOLD", "quantity": 0,
                "reasoning": f"Waiting. RSI={rsi:.1f}, MACD={macd_diff:.4f}"}

    except Exception as e:
        return {"action": "HOLD", "quantity": 0, "reasoning": f"Error: {e}"}
