from logging import exception
from enum import Enum
from models import resource
from datetime import time
from models.date import Date
from models.resource import Resource

class Event:
    def __init__(self, name, description, start:time, end:time):
        self.name = name
        self.description = description
        self.start_event = start
        self.end_event = end
        self.list_resources=set()
        self.list_hours=set()
        self.resource=resource
        self.dates=[]

    def add_resource(self, resource:Resource):
        self.list_resources.add(resource) if resource not in self.list_resources else None

    def add_date(self, date_add:Date):
        if date_add.start_date<self.start_event or date_add.end_date>self.end_event:
            raise ValueError(f"El servicio de {self.name} está disponible de {self.start_event} a {self.end_event}")
        for date in self.dates:
            if date.start_date<date_add.end_date and date.end_date>date_add.start_date:
                raise ValueError(f"Cita no disponible, Citas disponibles: {self.search_dates()}")
        self.dates.append(date_add)
        self.list_hours.add((date_add.start_date.hour,date_add.end_date.hour))


    def search_dates(self):
        cur=[num for num in range(self.start_event.hour,self.end_event.hour+1)]
        ans=[]
        min_value=min(self.list_hours)
        max_value=max(self.list_hours)
        h1=cur.index(min_value)
        h2=cur.index(max_value)
        cur=cur[:h1]+cur[h2+1:]
        if len(cur)>0:
            return [time(num,0) for num in cur]
        else:
            return f"No hay Citas disponibles en {self.name}"

class TypeEvent(Enum):
    CirugiasProgramadas=Event("Cirugias Programadas",
        "Planes de cirugía solo electivas", time(8,30),time(16,0))

