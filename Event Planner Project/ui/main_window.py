from core import event_manager
import tkinter as tk
from tkinter import ttk
from models.planificador import Planificador
from ui.event_dialog import EventDialog

class MainWindow:
    def __init__(self,root):
        self.root=root
        self.root.title("Sistema de Gestion Hospitalaria")
        self.root.geometry("1000x700")
        self.planificador=Planificador()
        self.setup_iu()
        self.root.mainloop()
    def setup_iu(self):
        main_frame=ttk.Frame(self.root, padding="10")
        main_frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        btn_frame=ttk.Frame(main_frame)
        btn_frame.grid(row=0, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="➕ Nuevo Evento", command=self.open_event_dialog).pack(side=tk.LEFT,padx=5)

    def open_event_dialog(self):
        dialog=EventDialog(self.root,self.planificador,self.refresh_events)
        self.root.wait_window(dialog.top)

    def refresh_events(self):
        return self.planificador.list_event
