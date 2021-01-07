import datetime

from castlib.event import Event
from castlib.util import format_currency

import yfinance as yf

class StockGrant(Event):
    
    def __init__(self, *args, total_shares, ticker, date, tax_rate=0.4):
        data = yf.Ticker(ticker)
        df = data.history(period="1d")

        self.latest_price = df["Close"][0]
        self.shares_this_year = total_shares/4
        self.ticker = ticker

        grant_value = self.shares_this_year * self.latest_price * (1-tax_rate)
        
        super().__init__(name=f"{ticker} Stock Grant", amount=grant_value, date=date)
        
    
    def __str__(self):
        return f"""Yearly RSU grant is currently worth: {format_currency(self.shares_this_year * self.latest_price)}
{self.ticker} is currently worth {format_currency(self.latest_price)}"""
