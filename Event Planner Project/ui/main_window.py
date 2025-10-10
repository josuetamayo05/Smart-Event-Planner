from core import event_manager
import tkinter as tk
from tkinter import ttk
from models.planificador import Planificador
from ui.event_dialog import EventDialog

class MainWindow:
    def __init__(self,root):
        self.root=root
        self.root.title("Sistema de Gestion Hospitalaria")
        self.root.geometry("500x500")
        self.planificador=Planificador()
        self.setup_iu()
        self.root.mainloop()
    def setup_iu(self):
        main_frame=ttk.Frame(self.root, padding="10")
        main_frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        btn_frame=ttk.Frame(main_frame)
        btn_frame.grid(row=0, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="➕ Nuevo Evento", command=self.open_event_dialog).pack(side=tk.LEFT,padx=5)
        ttk.Button(btn_frame, text=" Lista de Eventos", command=self.refresh_events()).pack(side=tk.LEFT,padx=5)
        ttk.Button(btn_frame, text="🔍 Buscar Hueco", command=self.find_slot).pack(side=tk.LEFT,padx=5)
        ttk.Button(btn_frame, text="💾 Guardar", command=self.save_data).pack(side=tk.LEFT,padx=5)

        # Lista Eventos
        self.tree=ttk.Treeview(main_frame, columns=('Hora inicio', 'Hora fin', 'Paciente', 'Recursos'), show="headings")
        self.tree.heading('Hora inicio', text='Hora inicio')
        self.tree.heading('Hora fin', text='Hora fin')
        self.tree.heading('Paciente', text='Paciente')
        self.tree.heading('Recursos', text='Recursos')
        self.tree.grid(row=1,column=0, sticky=(tk.W, tk.E, tk.N, tk.S),pady=10)

        # Barra de Estado
        self.status_var=tk.StringVar(value="Listo")
        status_bar=ttk.Label(main_frame, textvariable=self.status_var,relief=tk.SUNKEN)
        status_bar.grid(row=1,column=1, sticky=(tk.W, tk.E))

    def open_event_dialog(self):
        dialog=EventDialog(self.root,self.planificador,self.refresh_events)
        self.root.wait_window(dialog.top)

    def find_slot(self):
        pass

    def refresh_events(self):
        return self.planificador.list_event

    def save_data(self):
        pass
