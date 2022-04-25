import datetime

from dateutil.relativedelta import relativedelta

class Event:
    name = ""
    date = datetime.date.today()
    amount = 0

    def __init__(self, *args, name, date, amount, end=datetime.date.today() + relativedelta(years=50)):
        if type(date) != datetime.date:
            raise Error("Date must be datetime.date")
        
        self.name = name
        self.date = date
        self.amount = amount
        self.end = end

    def __str__(self):
        return f'{self.name} for {self.amount} on {self.date}'
    
    def __repr__(self):
        return str(self)
    
    def __dict__(self):
        return {
            "name": self.name,
            "date": self.date.__str__(),
            "amount": self.amount
        }
            
    def get_recurring(self, *args, delta):
        c_event = self
        events = []
                
        while c_event.date <= self.end:
            events.append(c_event)
            c_event = Event(name=self.name, date=c_event.date + delta, amount=self.amount)
        
        return events
    
    @property
    def semi_monthly(self):
        last = Event.fromevent(self)
        middle = Event.fromevent(self)

        last.date = last.date.replace(day=1)
        middle.date = middle.date.replace(day=15)
            
        return last.get_recurring(delta=relativedelta(months=1, days=-1)) + middle.get_recurring(delta=relativedelta(months=1))

    @property
    def monthly(self):
        return self.get_recurring(delta=relativedelta(months=1))
    
    @property
    def weekly(self):
        return self.get_recurring(delta=relativedelta(weeks=1))
    
    @property
    def yearly(self):
        return self.get_recurring(delta=relativedelta(years=1))
    
    @classmethod
    def fromevent(self, event):
        return Event(name=event.name, amount=event.amount, date=event.date)

    @classmethod
    def fromdict(self, event):
        return Event(name=event["name"], amount=event["amount"], date=datetime.date.fromisoformat(event["date"]))
    
    @classmethod
    def easy(self, name, amount, date):
        return Event(name=name, amount=amount, date=date)
    
    @classmethod
    def today(self, name, amount):
        return Event(name=name, amount=amount, date=datetime.date.today())