from castlib.cast import Cast
from castlib.prop import Prop
from castlib.util import format_currency, format_percent, format_number

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

import math
import time

import pandas as pd
from datetime import date

class Reporter:
    cast = Cast()
    _dpi = 75
    _size = (12, 8)
    
    def __init__(self, cast):
        self.cast = cast
    
    @property
    def size(self):
        return self._size
    
    @size.setter
    def size(self, value):
        self._size = value
        
    def figure(self):
        return plt.subplots(figsize=self.size, dpi=self._dpi)
        
    def running_balance(self, new_rates=None, props=None, mark_today=False, title="Running Balance", annotate=None):
        if not props:
            props = []
            
        if not annotate:
            annotate = []

        # make sure we show the data without props
        props = [Prop([], name="Default")] + props
            
        fig, ax = self.figure()
        formatter = ticker.StrMethodFormatter('${x:,.0f}')
        ax.yaxis.set_major_formatter(formatter)
        
        for prop in props:
            self.cast.with_prop(prop)

            dates, balances = self.cast.running_balance(split=True)
            date_times = [time.mktime(d.timetuple()) for d in dates]
            plt.plot(date_times, balances, label=f'{prop.name}')
            
            if mark_today:
                annotate.append(date.today())

            if annotate:
                for a in annotate:
                    running_balance = self.cast.running_balance()
                    today = time.mktime(a.timetuple())
                    balance = running_balance[a]
                    plt.annotate(format_currency(balance), # this is the text
                                 (today,balance), # this is the point to label
                                 textcoords="offset points", # how to position the text
                                 xytext=(0,10), # distance from text to points (x,y)
                                 ha='center') # horizontal alignment can be left, right or center
                    plt.scatter(today, balance, s=20)

            if new_rates:
                for new_rate in new_rates:
                    old_rate = self.cast.apr

                    self.cast.at_apr(new_rate)
                    dates, balances = self.cast.running_balance(split=True)
                    date_times = [time.mktime(d.timetuple()) for d in dates]
                    plt.plot(date_times, balances, label=f'{prop.name}@{new_rate}%')

                    self.cast.at_apr(old_rate)
            self.cast.clear_props()
        
        cut_out = math.floor(len(date_times)/20)
        plt.xticks(date_times[::cut_out], labels=dates[::cut_out], rotation=30);
        plt.title(title)
        plt.legend()
        return self
    
    def tx_pie(self):
        fig = self.figure()
        events = dict()
        total = 0
        negative_events = sorted([e for e in self.cast.events if e.amount < 0],key=lambda e: e.amount)
        for event in negative_events:
            if event.name not in events:
                events[event.name] = 0
            events[event.name] += event.amount
            total += event.amount
            
        plt.pie([(abs(events[event]/total)) for event in events], labels=[event for event in events])
        
    def days_till_broke(self, props):
        if not props:
            props = []

        # make sure we show the data without props
        props = [Prop([], name="Default")] + props
        
        simulation_results = dict()
        
        for prop in props:
            self.cast.with_prop(prop)
            simulation_results[prop.name] = self.cast.first_day_under(0)
            self.cast.clear_props()
            
        base = ((simulation_results["Default"] - date.today()).days / 30)
        longest = base
        
        results = []

        for scenario in simulation_results:
            months_til_broke = ((simulation_results[scenario] - date.today()).days / 30)

            difference = months_til_broke - base

            if difference > 0:
                difference = "+" + str(difference)
            else:
                difference = "-" + str(difference)

            if months_til_broke > longest:
                longest = months_til_broke
            
            results.append([scenario, str(months_til_broke)[:4], difference[:4]])
            
        return results
    
    def n_day_moving_average(self, n):
        dates, balances = self.cast.running_balance(change_only=True, split=True)
        
        if len(dates) <= n:
            return []
        
        included_balances = dates[:n]
        balances = balances[n:]
        moving_average = []
        
        for i in range(len(dates)):
            moving_average.append([dates[i], sum(included_balances) / n])
            included_balances.pop(0)
            included_balances.push(balances.pop(0))
            print(included_balances)
            
        return moving_average
    
    
    def milestones(self, filter_return=True):        
        # milestones in thousands
        milestones = [10, 20, 50, 75, 100, 150, 250, 300, 400, 500, 750, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 10000] 
        data = []
        
        for milestone in milestones:
            milestone *= 1000
            entry = {
                "amount": format_currency(milestone)
            }
            if milestone <= self.cast.balance:
                entry["is_passed"] = True
                entry["date"] = None
            
            else:
                entry["is_passed"] = False
                d, balance = self.cast.first_day_over(milestone, return_balance=True)
                entry["date"] = d if d > d.today() else None
                entry["balance"] = format_currency(balance)
                # time until met
                years = ((d - d.today()).days)/365
                entry["years_until"] = format_number(years)
                
                if years < 1:
                    entry["years_until"] = format_percent(years)
                
            data.append(entry)
            
        df = pd.DataFrame.from_dict(data)
        
        if filter_return:
            df = df[(df["date"].notnull()) | (df["is_passed"])]
            
        return df