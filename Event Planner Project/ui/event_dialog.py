from tkinter import ttk
import tkinter as tk

class EventDialog:
    def __init__(self,root, planificador,refresh_events):
        self.root=root
        self.planificador=planificador
        self.refresh_events=refresh_events
        self.top=tk.Toplevel(root)
        self.top.title("Planificar Evento Nuevo")
        self.top.geometry("500x400")
        self.setup_form()

    def setup_form(self):
        ttk.Label(self.top, text="Nombre del Paciente:").grid(row=0,column=0,sticky=tk.W,padx=5,pady=5)
        self.patient_entry = ttk.Entry(self.top,width=30)
        self.patient_entry.grid(row=0,column=1,padx=5,pady=5)
        ttk.Button(self.top,text="Planificar",command=self.shedule_event).grid(row=10,column=0,sticky=tk.W,pady=10)

    def shedule_event(self):
        pass



