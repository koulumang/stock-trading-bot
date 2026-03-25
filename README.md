# Stock Trading Bot

A paper-trading bot that uses technical indicators to simulate buy/sell decisions on stocks.

## Features

- Real-time stock price fetching
- Strategy based on RSI, MACD, Bollinger Bands, and SMAs
- Stop-loss (-1.5%) and take-profit (+3%) management
- Virtual portfolio with cash and P&L tracking
- Trade history logged to `trades.json`
- Two interfaces:
  - **CLI** — run directly in the terminal
  - **Web UI** — Flask dashboard at `localhost:5001`

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

**CLI:**
```bash
python main.py
```

**Web UI:**
```bash
python app.py
```
Then open [http://localhost:5001](http://localhost:5001)
