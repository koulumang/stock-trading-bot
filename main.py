import threading
from config import SYMBOLS
from trader import run_trading_loop

PERIODS    = ['1mo', '3mo', '6mo', '1y']
INTERVALS  = ['1d', '1h']

def get_user_selection():
    while True:
        print("\nSelect Stock Exchange:")
        for i, (exchange, (sym, cur)) in enumerate(SYMBOLS.items(), 1):
            print(f"{i}. {exchange} ({sym})")
        choice = input("Enter choice: ").strip()
        keys = list(SYMBOLS.keys())
        if choice.isdigit() and 1 <= int(choice) <= len(keys):
            return SYMBOLS[keys[int(choice) - 1]]
        print("Invalid choice. Try again.")

def run_backtest_cli():
    from backtest import run_backtest
    symbol, currency = get_user_selection()

    print("\nBacktest period:")
    for i, p in enumerate(PERIODS, 1):
        print(f"  {i}. {p}")
    pc = input("Enter choice [default 2 = 3mo]: ").strip()
    period = PERIODS[int(pc) - 1] if pc.isdigit() and 1 <= int(pc) <= len(PERIODS) else '3mo'

    print("\nBar interval:")
    for i, iv in enumerate(INTERVALS, 1):
        print(f"  {i}. {iv}")
    ic = input("Enter choice [default 1 = 1d]: ").strip()
    interval = INTERVALS[int(ic) - 1] if ic.isdigit() and 1 <= int(ic) <= len(INTERVALS) else '1d'

    print(f"\nRunning backtest for {symbol} over {period} ({interval} bars)…", flush=True)
    result = run_backtest(symbol, currency, period, interval)

    if 'error' in result:
        print(f"Error: {result['error']}")
        return

    cur = result['currency']
    print(f"\n{'='*40}")
    print(f"  Backtest Results — {result['symbol']} ({result['period']}/{result['interval']})")
    print(f"{'='*40}")
    print(f"  Initial cash   : {cur}{result['initial_cash']:,.2f}")
    print(f"  Final value    : {cur}{result['final_value']:,.2f}")
    print(f"  Total return   : {result['total_return_pct']:+.2f}%")
    print(f"  Win rate       : {result['win_rate_pct']:.1f}%")
    print(f"  Sharpe ratio   : {result['sharpe_ratio']:.3f}")
    print(f"  Max drawdown   : {result['max_drawdown_pct']:.2f}%")
    print(f"  Total trades   : {result['total_trades']}  (B:{result['buy_trades']} S:{result['sell_trades']})")
    print(f"  Bars analysed  : {result['bars_analysed']}")
    print(f"{'='*40}\n")

def main():
    print("\nMode:")
    print("  1. Live paper trading")
    print("  2. Backtest")
    mode = input("Enter choice [default 1]: ").strip()

    if mode == '2':
        run_backtest_cli()
        return

    symbol, currency = get_user_selection()
    print(f"Starting trader for {symbol} ({currency})... Press Ctrl+C to stop.", flush=True)

    stop_event = threading.Event()
    try:
        run_trading_loop(symbol, currency, stop_event)
    except KeyboardInterrupt:
        stop_event.set()
        print("\nStopped.", flush=True)

if __name__ == "__main__":
    main()
