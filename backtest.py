import pandas as pd
from data_fetcher import get_historic_data
from portfolio import Portfolio
from strategy import get_trade_decision
from config import INITIAL_CASH_USD, INITIAL_CASH_INR

WARMUP_BARS = 15  # bars needed for indicators (RSI/BB/MACD) to stabilise


def run_backtest(symbol, currency='$', period='3mo', interval='1d', initial_cash=None):
    if initial_cash is None:
        initial_cash = INITIAL_CASH_INR if currency == '₹' else INITIAL_CASH_USD

    history = get_historic_data(symbol, period=period, interval=interval)
    if history.empty or len(history) < WARMUP_BARS + 2:
        return {"error": f"Not enough data for {symbol} ({period}/{interval})"}

    portfolio   = Portfolio(initial_cash=initial_cash, currency=currency)
    port_values = []
    trades      = []

    for i in range(WARMUP_BARS, len(history)):
        window        = history.iloc[:i + 1]
        current_price = float(window['Close'].iloc[-1])

        status = portfolio.get_status({symbol: current_price})
        port_values.append(status['total_value'])

        decision = get_trade_decision(symbol, window, current_price, status, currency)
        action   = decision.get('action', 'HOLD')
        quantity = int(decision.get('quantity', 0))

        if action == 'BUY' and quantity > 0:
            # snapshot avg before buying (will be the new avg after; we want entry price)
            avg_buy = current_price
            success, _ = portfolio.buy(symbol, current_price, quantity)
            if success:
                trades.append({'action': 'BUY', 'price': current_price,
                               'quantity': quantity, 'avg_buy': avg_buy})

        elif action == 'SELL' and quantity > 0:
            avg_buy = 0.0
            for h in status['holdings_summary']:
                if h['symbol'] == symbol:
                    avg_buy = h['avg_price']
                    break
            success, _ = portfolio.sell(symbol, current_price, quantity)
            if success:
                trades.append({'action': 'SELL', 'price': current_price,
                               'quantity': quantity, 'avg_buy': avg_buy})

    # Final mark-to-market
    final_price  = float(history['Close'].iloc[-1])
    final_status = portfolio.get_status({symbol: final_price})
    port_values.append(final_status['total_value'])

    values         = pd.Series(port_values, dtype=float)
    daily_returns  = values.pct_change().dropna()

    # Win rate — percentage of SELL trades where exit > entry (fees included in portfolio)
    sell_trades = [t for t in trades if t['action'] == 'SELL']
    wins        = sum(1 for t in sell_trades if t['price'] > t['avg_buy'])
    win_rate    = (wins / len(sell_trades) * 100) if sell_trades else 0.0

    # Annualised Sharpe (risk-free ≈ 5 % p.a.)
    risk_free_per_bar = 0.05 / 252
    if daily_returns.std() > 0:
        bars_per_year = 252 if interval == '1d' else (252 * 390 if interval == '1m' else 252 * 78)
        sharpe = ((daily_returns.mean() - risk_free_per_bar)
                  / daily_returns.std()
                  * (bars_per_year ** 0.5))
    else:
        sharpe = 0.0

    # Max drawdown
    peak         = values.cummax()
    drawdown     = (values - peak) / peak
    max_drawdown = float(drawdown.min() * 100)

    total_return = (final_status['total_value'] - initial_cash) / initial_cash * 100

    return {
        "symbol":           symbol,
        "period":           period,
        "interval":         interval,
        "currency":         currency,
        "initial_cash":     round(initial_cash, 2),
        "final_value":      round(final_status['total_value'], 2),
        "total_return_pct": round(total_return, 2),
        "win_rate_pct":     round(win_rate, 1),
        "sharpe_ratio":     round(sharpe, 3),
        "max_drawdown_pct": round(max_drawdown, 2),
        "total_trades":     len(trades),
        "buy_trades":       len([t for t in trades if t['action'] == 'BUY']),
        "sell_trades":      len(sell_trades),
        "bars_analysed":    len(port_values),
    }
