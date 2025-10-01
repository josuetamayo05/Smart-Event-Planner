import tkinter as tk
from ui.main_window import MainWindow
from core.event_manager import EventManager
from models.date import Date
from datetime import time

def main():
    event=EventManager.CirugiasProgramadas
    dat=Date("Hola soy mari quiero ser feliz",time(8,30), time(10,00))
    dat2=Date("quiero turno",time(10,00), time(12,0))
    event.addDate(dat)
    event.addDate(dat2)
    print(event.search_disponible_dates())

if __name__ == '__main__':
    main()