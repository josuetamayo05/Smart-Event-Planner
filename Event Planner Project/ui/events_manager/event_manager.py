from tkinter.ttk import *
from tkinter import *
import tkinter.messagebox
from PIL import ImageTk, Image
import sqlite3
import os

conn=sqlite3.connect('../../data/database.db')
cursor=conn.cursor()

class EventDialog:
    def __init__(self, master):
        self.master = master
        self.setup_ui()

    def setup_ui(self):
        self.main_frame = Frame(self.master,bg='#f0f8ff')
        self.main_frame.pack(fill='both',expand=True,padx=10,pady=10)
        title_label=Label(self.main_frame,text="🏥 GESTIÓN DE EVENTOS Y RECURSOS HOSPITALARIOS",
                          font=('Arial',16,'bold'),bg='#2c3e50',fg='white',padx=10,pady=10)
        title_label.pack(fill='x',pady=(0,20))
        self.setup_controls()
        self.setup_notebook()

    def setup_controls(self):
        controls_frame=Frame(self.main_frame,bg='#f0f8ff')
        controls_frame.pack(fill='x',pady=(0,10))

        # control panel
        search_frame=Frame(controls_frame,bg='#f0f8ff')
        search_frame.pack(side='left',padx=(0,20))

        Label(search_frame,text='🔍 Buscar:',font=('Arial',12)).pack(side='left')
        self.search_entry=Entry(search_frame,font=('Arial',12,'bold'),width=20)
        self.search_entry.pack(side='left',padx=5)
        self.search_entry.bind('<KeyRelease>',self.filter_resources)

        new_event_btn=Button(controls_frame,text="➕ Nuevo Evento",command=self.new_event_dialog,bg='blue',fg='white',font=('Arial',12,'bold'),padx=15)
        new_event_btn.pack(side='right')

    def setup_notebook(self):
        self.notebook=Notebook(self.main_frame)
        self.notebook.pack(fill='both',expand=True)

        self.resources_tab=Frame(self.notebook,bg='#f0f8ff')
        self.events_tab=Frame(self.notebook,bg='#f0f8ff')
        self.calendar_tab=Frame(self.notebook,bg='#f0f8ff')

        self.notebook.add(self.resources_tab,text='Recursos')
        self.notebook.add(self.events_tab,text='Eventos')
        self.notebook.add(self.calendar_tab,text='Calendario')

        self.setup_resources_tab()
        self.setup_events_tab()
        self.setup_calendar_tab()

    def setup_resources_tab(self):
        filter_frame=Frame(self.resources_tab,bg='#f0f8ff')
        filter_frame.pack(side='x',padx=(0,10))

        Label(filter_frame,text="Filtrar por tipo", bg='f0f8ff').pack(side='left')
        self.filter_var=StringVar(value="Todos")

        filter_options=["Todos","Quirófanos","Personal","Equipos"]
        for option in filter_options:
            Radiobutton(filter_frame,text=option,variable=self.filter_var,value=option,bg='f0f8ff',
                        command=self.filter_resources).pack(side='left')

        #Frame for Resources
        resources_contains=Frame(self.resources_tab)
        resources_contains.pack(fill='both',expand=True)

        # Canvas and Scrollbar
        self.canvas=Canvas(resources_contains,bg='#f0f8ff',highlightthickness=0)
        scrollbar=Scrollbar(resources_contains,orient="vertical",command=self.canvas.yview)
        self.scrollable_frame=Frame(self.canvas,bg='#f0f8ff')

        self.scrollable_frame.bind("<Configure>",lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0,0),self.scrollable_frame,anchor='nw')
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left",fill="both",expand=True)
        scrollbar.pack(side="right",fill="y")

    def setup_events_tab(self):
        pass
    def setup_calendar_tab(self):
        pass

    def new_event_dialog(self):
        pass

    def filter_resources(self):
        pass



def init():
    event=Tk()
    window=EventDialog(event)
    event.geometry("1200x720+0+0")
    event.resizable(0, 0)
    event.mainloop()

init()
