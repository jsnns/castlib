from castlib.cast import Cast
from castlib.prop import Prop

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

import math
import time

class Reporter:
    cast = Cast()
    _dpi = 200
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
        
    def running_balance(self, new_rates=None, props=None):
        if not props:
            props = []
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
        plt.legend()
        return self
    
    def tx_pie(self):
        fig = self.figure()
        negative_events = sorted([e for e in self.cast.events if e.amount < 0],key=lambda e: e.amount)
        plt.pie([e.amount * -1 for e in negative_events], labels=[e.name for e in negative_events])