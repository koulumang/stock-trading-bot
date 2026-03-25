import threading
from config import SYMBOLS
from trader import run_trading_loop

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

def main():
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
