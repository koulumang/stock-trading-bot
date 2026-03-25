TRANSACTION_FEE_PCT = 0.001  # 0.1% per trade

class Portfolio:
    def __init__(self, initial_cash=10000.0, currency='$'):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.currency = currency
        self.holdings = {}  # symbol -> {'quantity': int, 'avg_price': float}
        self.trade_history = []

    def buy(self, symbol, price, quantity):
        cost = price * quantity * (1 + TRANSACTION_FEE_PCT)
        if cost > self.cash:
            return False, "Insufficient funds"
        
        self.cash -= cost
        
        if symbol not in self.holdings:
            self.holdings[symbol] = {'quantity': quantity, 'avg_price': price}
        else:
            # Calculate weighted average price
            current_qty = self.holdings[symbol]['quantity']
            current_avg = self.holdings[symbol]['avg_price']
            new_qty = current_qty + quantity
            new_avg = ((current_qty * current_avg) + (quantity * price)) / new_qty
            
            self.holdings[symbol]['quantity'] = new_qty
            self.holdings[symbol]['avg_price'] = new_avg

        self.trade_history.append({
            "action": "BUY",
            "symbol": symbol,
            "price": price,
            "quantity": quantity,
            "timestamp": None # To be filled by caller or datetime.now()
        })
        return True, f"BUY executed: {quantity} {symbol} at {self.currency}{price:.2f}"

    def sell(self, symbol, price, quantity):
        if symbol not in self.holdings:
            return False, "No holdings for symbol"
            
        current_qty = self.holdings[symbol]['quantity']
        
        if current_qty < quantity:
            return False, "Insufficient holdings"
        
        revenue = price * quantity * (1 - TRANSACTION_FEE_PCT)
        self.cash += revenue
        
        self.holdings[symbol]['quantity'] -= quantity
        
        if self.holdings[symbol]['quantity'] == 0:
            del self.holdings[symbol]
            
        self.trade_history.append({
            "action": "SELL",
            "symbol": symbol,
            "price": price,
            "quantity": quantity,
            "timestamp": None
        })
        return True, f"SELL executed: {quantity} {symbol} at {self.currency}{price:.2f}"

    def get_total_value(self, current_prices):
        """
        Calculate total portfolio value (cash + holdings value).
        current_prices: dict of symbol -> price
        """
        holdings_value = 0
        for symbol, data in self.holdings.items():
            price = current_prices.get(symbol, 0)
            holdings_value += data['quantity'] * price
        return self.cash + holdings_value

    def get_status(self, current_prices):
        total_value = self.get_total_value(current_prices)
        total_profit_loss = total_value - self.initial_cash
        
        # Calculate details for each holding
        holdings_details = []
        for symbol, data in self.holdings.items():
            current_price = current_prices.get(symbol, 0)
            qty = data['quantity']
            avg_price = data['avg_price']
            current_val = qty * current_price
            invested_val = qty * avg_price
            unrealized_pl = current_val - invested_val
            
            holdings_details.append({
                'symbol': symbol,
                'quantity': qty,
                'avg_price': avg_price,
                'current_price': current_price,
                'current_value': current_val,
                'unrealized_pl': unrealized_pl
            })

        return {
            "cash": self.cash,
            "holdings_summary": holdings_details, # Detailed list
            "total_value": total_value,
            "profit_loss": total_profit_loss
        }
