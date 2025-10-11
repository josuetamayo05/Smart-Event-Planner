import datetime
from tkinter.ttk import *
from tkcalendar import Calendar
from core import event_manager
import tkinter as tk
from tkinter import *
from models.planificador import Planificador
from ui.event_dialog import EventDialog


class MainWindow:
    def __init__(self,root):
        self.root=root
        self.root.title("Sistema de Gestion Hospitalaria")
        self.left=Frame(root, width=800, height=720,bg='white')
        self.left.pack(side=LEFT)
        self.right=Frame(root, width=400, height=720,bg='steelblue')
        self.right.pack(side=RIGHT)
        self.cal=Calendar(self.left,year=2025,month=1,day=1)
        self.cal.pack(side=TOP)

        self.heading=Label(self.left,text="Registro del Paciente",font=('arial 30 bold'),fg='black',bg='white')
        self.heading.place(x=30,y=0)

        ## LABEls for the windows
        self.name=Label(self.left,text="Nombre del Paciente",font=('arial 12 bold'),fg='black',bg='white')
        self.name.place(x=30,y=105)

        self.age=Label(self.left,text="Edad",font=('arial 12 bold'),fg='black',bg='white')
        self.age.place(x=30,y=140)

        self.location=Label(self.left,text="Dirección",font=('arial 12 bold'),fg='black',bg='white')
        self.location.place(x=30,y=175)

        self.number=Label(self.left,text="Número de teléfono",font=('arial 12 bold'),fg='black',bg='white')
        self.number.place(x=30,y=210)

        self.events=Label(self.left,text="Tipo de Consulta",font=('arial 12 bold'),fg='black',bg='white')
        self.events.place(x=29,y=245)

        self.day=Label(self.left,text="Fecha", font=('arial 12 bold'),fg='black',bg='white')
        self.day.place(x=31,y=280)

        ## Entry all labels
        self.num_ent=Entry(self.left,width=80)
        self.num_ent.place(x=250,y=110)

        self.age_ent=Entry(self.left,width=80)
        self.age_ent.place(x=250,y=145)

        self.location_ent=Entry(self.left,width=80)
        self.location_ent.place(x=250,y=180)

        self.number_ent=Entry(self.left,width=80)
        self.number_ent.place(x=250,y=215)

        events=["Anestesiologia","Cirugia","Pediatria"]
        self.combo_events=Combobox(self.left,values=events)
        self.combo_events.place(x=250,y=250)

        days=["Lunes","Martes","Miercoles","Jueves","Viernes","Sabado","Domingo"]
        self.combo_days=Combobox(self.left,values=days)
        self.combo_days.place(x=250,y=285)

    # def select_date(self):
    #     def get_date():
    #         date_sel=cal.get_date()



root=Tk()
window=MainWindow(root)
root.geometry("1200x720+0+0")
root.resizable(False,False)
root.mainloop()
