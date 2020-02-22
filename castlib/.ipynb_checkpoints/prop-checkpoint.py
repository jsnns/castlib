class Prop:
    def __init__(self, events, name=""):
        self.events = events
        self.name = name
        
    def __add__(self, other):
        return Prop(self.events + other.events, name=f'{self.name} + {other.name}')