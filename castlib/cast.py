from dateutil.relativedelta import relativedelta

import datetime
import time
import json
import math

from castlib.prop import Prop
from castlib.event import Event

def get_event_timestamp(event):
    return time.mktime(event.date.timetuple())

class Cast:
    _report = None

    def __init__(self, *args, start=datetime.date.today(), enddelta=relativedelta(years=1), balance=0, apr=None):
        self.events = []
        self.props = []
        self.start = start
        self.end = (self.start + enddelta)
        self.balance = balance
        self.min_cash = None
        self.apr = apr
        
    @property
    def events(self):
        return self._events + self.props
    
    @events.setter
    def events(self, value):
        self._events = value
        return self
    
    @property
    def report(self):
        return self._report
    
    @property
    def last_day(self):
        return self.get_events_sorted_by_day(reverse=True)[0].date
    
    def set_min_cash(self, value):
        self.min_cash = value
        return self

    def at_apr(self, value):
        self.apr = value
        return self
        
    def report_with(self, R):
        self._report = R(cast=self)
        return self
        
    def end_after(self, days=0, weeks=0, months=0, years=0):
        self.end = (self.start + relativedelta(days=days, weeks=weeks, months=months, years=years))
        return self
    
    def trim(self):
        self.events = [event for event in self.events if event.date < self.end and event.date > self.start]
        return self
            
    
    # MAIN METHODS
    def add_event(self, event):
        if type(event) == list:
            for e in event:
                self._events.append(e)
            return self

        self._events.append(event)
        return self
    
    def with_props(self, props):
        for prop in props:
            self.with_prop(prop)
        return self
    
    def with_prop(self, prop):
        self.props += prop.events
        return self
    
    def clear_props(self):
        self.props = []
        return self
    
    def events_sorted_by_day(self, reverse=False):
        return sorted(self.events, key=get_event_timestamp, reverse=True)
    
    def events_by_day(self):
        events = self.events_sorted_by_day()
        by_day = {}
        
        for event in events:
            value = event.date
            
            if value not in by_day:
                by_day[value] = []
                
            by_day[value].append(event)
        
        return by_day
    
    def transactions_by_day(self):
        events = self.events_by_day()
        return {date: [event.amount for event in events[date]] for date in events}
    
    def running_balance(self, split=False, change_only=False):
        transactions = self.transactions_by_day()
        dates = sorted([date for date in transactions])
        
        balances = {}
        last_balance = self.balance
        
        current_date = self.start
        
        while current_date <= self.end:
            if current_date in dates:
                if change_only:
                    last_balance = sum(transactions[current_date])
                else:
                    last_balance += sum(transactions[current_date])
            elif change_only:
                last_balance = 0
                
            if self.apr and not change_only:
                rate =  1 + ((self.apr/100) / 365)
                if self.min_cash:
                    if last_balance > self.min_cash:
                        last_balance = ((last_balance - self.min_cash) * rate) + self.min_cash
                else:
                    last_balance *= rate
                
            balances[current_date] = last_balance
            current_date += datetime.timedelta(days=1)
            
        if (split):
            return [key for key in balances], [balances[key] for key in balances]
        
        return balances
    
    def min_n_balances(self, n):
        return sorted(self.running_balance(split=True)[1])[:n]
    

    def earliest_day(self, days):
        if not days:
            return datetime.datetime(1970, 1, 1).date()
        
        return days[0]
        
    
    def first_day_over(self, n, return_balance=False):
        balances = self.running_balance()
        days_over = [day for day in balances if balances[day] >= n]
        
        first_day_over = self.earliest_day(days_over)
        
        if return_balance and first_day_over:
            return self.earliest_day(days_over), self.running_balance()[first_day_over]
        
        return first_day_over
        
    
    def first_day_under(self, n):
        balances = self.running_balance()
        days_under = [day for day in balances if balances[day] <= n]
        
        return self.earliest_day(days_under)
        
    # SAVE AND LOAD
    def __dict__(self):
        return {
            "events": [event.__dict__() for event in self.events],
            "start": self.start.__str__(),
            "end": self.end.__str__(),
            "balance": self.balance,
            "apr": self.apr
        }
    
    def save(self, filename):
        contents = json.dumps(self.__dict__())
        with open(filename, "w") as file:
            file.write(contents)
        
        return self
    
    @classmethod
    def fromfile(self, filename):
        with open(filename) as file:
            data = json.load(file)
            
            start = datetime.datetime.strptime(data["start"], "%Y-%m-%d").date()
            end = datetime.datetime.strptime(data["end"], "%Y-%m-%d").date()

            new_cast = Cast(balance=data["balance"], start=start)
            new_cast.end = end
            
            if "apr" in data:
                new_cast.at_apr(data["apr"])
            
            events = [Event.fromdict(e) for e in data["events"]]
            new_cast.add_event(events)
            
            return new_cast