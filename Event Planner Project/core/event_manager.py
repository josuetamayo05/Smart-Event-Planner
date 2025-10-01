from models.event import Event
from datetime import time
class EventManager:
    CirugiasProgramadas = Event("Cirugias Programadas",
        "Planes de cirugía solo electivas", time(8, 30), time(16, 0))
