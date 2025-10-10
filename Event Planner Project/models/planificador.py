from models.Events.event import Event
from datetime import time
from models.resource import Resource
class Planificador:
    def __init__(self):
        self.list_event=[]
        self.list_resources=[]
        self.initial_hour=time(7,30)
        self.final_hour=time(19,0)
    def add_event(self,event:Event):
        if event.start_event<self.initial_hour or event.end_event>self.final_hour:
            raise ValueError(f"❌ Error: el horario del hospital está entre {self.initial_hour} y {self.final_hour}")

        self.list_event.append(event)

    def add_resource_to_event(self,resource:Resource,event:Event):
        if resource.is_used:
            raise ValueError("El objeto está siendo usado para otra función")
        self.list_resources.append(resource)


