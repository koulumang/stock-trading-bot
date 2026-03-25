from portfolio import Portfolio

def test_portfolio():
    p = Portfolio(initial_cash=10000.0)
    
    print("Initial Cash:", p.cash)
    
    # Buy 10 shares at 100
    p.buy("AAPL", 100.0, 10)
    print("\nBought 10 AAPL @ 100")
    status = p.get_status({"AAPL": 105.0})
    print("Status after buy 1:", status['holdings_summary'][0])
    assert status['holdings_summary'][0]['quantity'] == 10
    assert status['holdings_summary'][0]['avg_price'] == 100.0
    assert status['holdings_summary'][0]['unrealized_pl'] == 50.0 # (105-100)*10
    
    # Buy 10 more shares at 110
    p.buy("AAPL", 110.0, 10)
    print("\nBought 10 AAPL @ 110")
    status = p.get_status({"AAPL": 110.0})
    print("Status after buy 2:", status['holdings_summary'][0])
    assert status['holdings_summary'][0]['quantity'] == 20
    assert status['holdings_summary'][0]['avg_price'] == 105.0 # (10*100 + 10*110) / 20 = 105
    assert status['holdings_summary'][0]['unrealized_pl'] == 100.0 # (110-105)*20
    
    # Sell 5 shares at 120
    p.sell("AAPL", 120.0, 5)
    print("\nSold 5 AAPL @ 120")
    status = p.get_status({"AAPL": 120.0})
    print("Status after sell:", status['holdings_summary'][0])
    assert status['holdings_summary'][0]['quantity'] == 15
    assert status['holdings_summary'][0]['avg_price'] == 105.0 # Avg price shouldn't change on sell
    assert status['holdings_summary'][0]['unrealized_pl'] == 225.0 # (120-105)*15
    
    print("\nAll tests passed!")

if __name__ == "__main__":
    test_portfolio()
