from enum import Enum

class Specialty(Enum):
    CIRUJANO="Cirujano"
    ANESTESIOLOGO= "Anestesiologo"
    ODONTOLOGO= "Odontologo"
    ENFERMERO= "Enfermero"
    PEDIATRA= "Pediatra"
    CARDIOLOGO= "Cardiologo"
    RADIOLOGO= "Radiologo"

class Shift(Enum):
    MATUTINO="Matutino"
    VESPERTINO="Vespertino"
    NOCTURNO="Nocturno"

class Worker:
    def __init__(self, name:str, specialty:Specialty,shift:Shift,work_schedule:tuple):
        self.name = name
        self.specialty = specialty
        self.shift = shift
        self.work_schedule = work_schedule
        self.available=True
        self.events_assign=[]
    def isAvailable(self,start,end):
        if self.work_schedule[0]<start or self.work_schedule[1]>end:
            return False
        for event in self.events_assign:
            if self.shedulesIntervene(start,end,event): return False
        return True

    def shedulesIntervene(self,start,end,event)->bool:
        return (start<event.end_event or end>event.start_event)
