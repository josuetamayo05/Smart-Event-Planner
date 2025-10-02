from models.Events.event import Event
from datetime import time
class Planificador:
    def __init__(self):
        self.list_event=[]
        self.list_resources=[]
        self.initial_hour=time(7,30)
        self.final_hour=time(19,0)
    def addEvent(self,event:Event,start_hour:time,end_hour:time):
        if start_hour<self.initial_hour or end_hour>self.final_hour:
            raise ValueError(f"❌ Error: el horario del hospital está entre {self.initial_hour} y {self.final_hour}")
        else: self.list_event.append(event)
