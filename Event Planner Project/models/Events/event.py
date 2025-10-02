from logging import exception
from enum import Enum
from models import resource
from datetime import time
from models import date

class Event:
    def __init__(self, name, description, start:time, end:time):
        self.name = name
        self.description = description
        self.start_event = start
        self.end_event = end
        self.list_resources=set()
        self.list_hours=set()
        self.resource=resource
        self.dates={}

    def addResource(self, resource):
        self.list_resources.add(resource) if resource not in self.list_resources else None

    def addDate(self, date:date.Date):
        if date.startDate<self.start_event or date.endDate>self.end_event:
            return print(f"El servicio de {self.name} está disponible a partir de {date.startDate} +hasta+ {date.endDate}")

        for i in range(date.startDate.hour, date.endDate.hour):
            if i in self.list_hours and i<date.endDate.hour:
                raise exception("A esta hora no hay turnos disponibles")

        self.dates[(date.startDate, date.endDate)] = date
        self.list_hours.add(date.startDate.hour),self.list_hours.add(date.endDate.hour)


    def search_disponible_dates(self):
        cur=[]
        for hour in range(self.start_event.hour, self.end_event.hour):
            if not hour in self.list_hours:
                cur.append(time(hour,0))
        return print(f"Horarios disponibles {[h for h in cur]}")

class TypeEvent(Enum):
    CirugiasProgramadas=Event("Cirugias Programadas",
        "Planes de cirugía solo electivas", time(8,30),time(16,0))

