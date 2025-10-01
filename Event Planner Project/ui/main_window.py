from core import event_manager
import tkinter as tk
from tkinter import ttk

class MainWindow:
    def __init__(self,_event_manager:event_manager.EventManager):
        self._event_manager= event_manager
        self.window = tk.Tk()
        self._window_configure()
        self._create_widgets()

    def _window_configure(self):
        self.window.title("Smart Event Planner")
        self.window.geometry("800x400")
        self.window.resizable(True,True)

    def _create_widgets(self):
        self.bottom=ttk.Button(self.window,text="Add Event",command=self._bottom_manage)
        self.bottom.pack()

    def _bottom_manage(self):
        events=self._event_manager.EventManager.list_events()
        print(f"Events: {events}")

    def execute(self):
        self.window.mainloop()