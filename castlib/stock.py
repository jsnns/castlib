import datetime

from castlib.event import Event
from castlib.util import format_currency

import yfinance as yf

class StockGrant:
    
    def __init__(self, *args, total_shares, ticker, first_year, tax_rate=0.4, years=4):
        data = yf.Ticker(ticker)
        df = data.history(period="1d")
        self.first_year = first_year
        self.years = years

        self.latest_price = df["Close"][0]
        self.shares_this_year = total_shares/years
        self.ticker = ticker

        self.grant_value = self.shares_this_year * self.latest_price * (1-tax_rate)
        
    @property
    def events(self):
        e = [
            Event(name=f"{self.ticker} Stock Grant", amount=self.grant_value, date=datetime.date(self.first_year, 12, 8))
        ]
        
        for year in range(self.first_year + 1, self.first_year + self.years):
            e += [
                Event(name=f"{self.ticker} Stock Grant", amount=self.grant_value/4, date=datetime.date(year, 3, 16)),
                Event(name=f"{self.ticker} Stock Grant", amount=self.grant_value/4, date=datetime.date(year, 6, 15)),
                Event(name=f"{self.ticker} Stock Grant", amount=self.grant_value/4, date=datetime.date(year, 9, 21)),
                Event(name=f"{self.ticker} Stock Grant", amount=self.grant_value/4, date=datetime.date(year, 12, 14))
            ]
        
        return e
        
    
    def __str__(self):
        return f"""Yearly RSU grant is currently worth: {format_currency(self.shares_this_year * self.years * self.latest_price)}
{self.ticker} is currently worth {format_currency(self.latest_price)}"""
