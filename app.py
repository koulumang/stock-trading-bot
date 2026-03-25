from flask import Flask, render_template, jsonify, request
import threading
import time
from datetime import datetime
from config import INITIAL_CASH_USD, INITIAL_CASH_INR, MAX_LOGS

app = Flask(__name__)

STATE_LOCK = threading.Lock()
TRADER_STATE = {
    "running": False,
    "symbol": "AAPL",
    "currency": "$",
    "price": 0.0,
    "cash": INITIAL_CASH_USD,
    "holdings": {},
    "profit_loss": 0.0,
    "logs": []
}

TRADER_THREAD = None
STOP_EVENT = threading.Event()

def log_message(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    with STATE_LOCK:
        TRADER_STATE["logs"].insert(0, {"timestamp": timestamp, "message": msg})
        if len(TRADER_STATE["logs"]) > MAX_LOGS:
            TRADER_STATE["logs"].pop()

def run_trader(symbol, currency):
    from config import INITIAL_CASH_USD, INITIAL_CASH_INR
    from trader import run_trading_loop

    initial_cash = INITIAL_CASH_INR if currency == '₹' else INITIAL_CASH_USD

    with STATE_LOCK:
        TRADER_STATE["running"]  = True
        TRADER_STATE["symbol"]   = symbol
        TRADER_STATE["currency"] = currency
        TRADER_STATE["cash"]     = initial_cash

    def on_update(status, price):
        with STATE_LOCK:
            TRADER_STATE["price"]       = price
            TRADER_STATE["cash"]        = status['cash']
            TRADER_STATE["holdings"]    = status['holdings_summary']
            TRADER_STATE["profit_loss"] = status['profit_loss']

    run_trading_loop(symbol, currency, STOP_EVENT, on_update=on_update, on_log=log_message)

    with STATE_LOCK:
        TRADER_STATE["running"] = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    with STATE_LOCK:
        return jsonify(TRADER_STATE)

@app.route('/api/start', methods=['POST'])
def start_trader():
    global TRADER_THREAD
    if TRADER_THREAD and TRADER_THREAD.is_alive():
        return jsonify({"status": "error", "message": "Already running"})

    data     = request.json or {}
    symbol   = data.get('symbol', 'AAPL').strip().upper()
    currency = data.get('currency', '$')

    if not symbol:
        return jsonify({"status": "error", "message": "Invalid symbol"})

    STOP_EVENT.clear()
    TRADER_THREAD = threading.Thread(target=run_trader, args=(symbol, currency), daemon=True)
    TRADER_THREAD.start()
    return jsonify({"status": "success"})

@app.route('/api/stop', methods=['POST'])
def stop_trader():
    STOP_EVENT.set()
    return jsonify({"status": "success"})

@app.route('/api/clear_logs', methods=['POST'])
def clear_logs():
    with STATE_LOCK:
        TRADER_STATE["logs"] = []
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
