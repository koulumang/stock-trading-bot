"""
Shared trading loop used by both main.py (CLI) and app.py (web).
"""
import time
import json
import os
from datetime import datetime

from data_fetcher import get_current_price, get_historic_data
from portfolio import Portfolio
from strategy import get_trade_decision
from config import INITIAL_CASH_USD, INITIAL_CASH_INR

TRADE_LOG_FILE = "trades.json"

def _append_trade(record):
    trades = []
    if os.path.exists(TRADE_LOG_FILE):
        with open(TRADE_LOG_FILE) as f:
            try:
                trades = json.load(f)
            except json.JSONDecodeError:
                trades = []
    trades.append(record)
    with open(TRADE_LOG_FILE, 'w') as f:
        json.dump(trades, f, indent=2)

def run_trading_loop(symbol, currency, stop_event, on_update=None, on_log=None):
    """
    Core trading loop.
    - stop_event: threading.Event — set it to stop the loop
    - on_update(status, price): optional callback for state updates
    - on_log(msg): optional callback for log messages
    """
    def log(msg):
        if on_log:
            on_log(msg)
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

    initial_cash = INITIAL_CASH_INR if currency == '₹' else INITIAL_CASH_USD
    portfolio = Portfolio(initial_cash=initial_cash, currency=currency)

    log(f"Starting trading for {symbol} ({currency})...")

    while not stop_event.is_set():
        try:
            current_price = get_current_price(symbol)
            if current_price is None:
                time.sleep(1)
                continue

            status = portfolio.get_status({symbol: current_price})

            if on_update:
                on_update(status, current_price)

            log(f"Price: {currency}{current_price:.2f} | P/L: {currency}{status['profit_loss']:.2f}")

            history_data = get_historic_data(symbol)

            if not history_data.empty:
                last_row = history_data.iloc[-1]
                log(f"RSI: {last_row.get('RSI', 0):.2f} | MACD_Diff: {last_row.get('MACD_DIFF', 0):.4f}")

            log("Analyzing Market...")
            decision = get_trade_decision(symbol, history_data, current_price, status, currency)

            action    = decision.get('action', 'HOLD')
            quantity  = int(decision.get('quantity', 0))
            reasoning = decision.get('reasoning', '')

            log(f"Strategy: {action} {quantity}. {reasoning}")

            if action == "BUY" and quantity > 0:
                success, msg = portfolio.buy(symbol, current_price, quantity)
                log(f"Trade: {msg}")
                if success:
                    _append_trade({"action": "BUY", "symbol": symbol, "price": current_price,
                                   "quantity": quantity, "timestamp": datetime.now().isoformat()})

            elif action == "SELL" and quantity > 0:
                success, msg = portfolio.sell(symbol, current_price, quantity)
                log(f"Trade: {msg}")
                if success:
                    _append_trade({"action": "SELL", "symbol": symbol, "price": current_price,
                                   "quantity": quantity, "timestamp": datetime.now().isoformat()})

            time.sleep(2)

        except Exception as e:
            log(f"Error: {e}")
            time.sleep(2)

    log("Trader stopped.")
