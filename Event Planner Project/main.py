import tkinter as tk

from services.workes import Worker, Specialty, Shift
from ui.main_window import MainWindow
from models.Events.event import *
from models.date import Date
from datetime import time
import json
from services import *

def main():
    cirugia=Event("Cirugia plastica","sdasda",time(8,0),time(12,0))
    dat=Date("Keilo","Cirugia plastica",time(8,0),time(9,0))
    da2=Date("heis","cirugia",time(9,0),time(11,0))
    cirugia.add_date(dat)
    cirugia.add_date(da2)
    cirugia.search_dates()
    fabio= Worker("Fabio",Specialty.ENFERMERO,Shift.MATUTINO,(time(8,0),time(16,0)))
    fabio.add_event(cirugia)
    print(fabio.isAvailable(time(9,0),time(10,0)))
if __name__ == '__main__':
    main()