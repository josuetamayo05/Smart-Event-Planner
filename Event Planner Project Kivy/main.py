from __future__ import annotations

import os

import dotenv
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager
from kivy.utils import platform

from kivymd.app import MDApp

from backend.database.database_manager import DatabaseManager
from backend.models.sheduler import Sheduler

from frontend.views.screens_manager import ScreensManager

from frontend.views.dashboard_screen import DashboardScreen
from frontend.views.events_screen import EventsScreen, EventCard
from frontend.views.resources_screen import ResourcesScreen
#from frontend.views.calendar_screen import CalendarScreen
from frontend.views.constraints_screen import ConstraintsScreen
from frontend.views.new_event_screen import NewEventScreen
#from widgets.calendar_widget import DayCalendar

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


class HospitalApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        db_path=os.getenv("HOSPITAL_DB_PATH", "database.json")
        self.db = DatabaseManager(db_path)
        self.sheduler = Sheduler(self.db)

    def build(self):
        self.title = "Planificador Inteligente Hospitalario"
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        Builder.load_file("hospital.kv")
        return ScreensManager()

    def toggle_theme_style(self):
        self.theme_cls.theme_style = (
            "Dark" if self.theme_cls.theme_style == "Light" else "Light"
        )

    def on_stop(self):
        self.db.save()

if __name__=="__main__":
    if platform in ("linux", "win", "macosx"):
        Window.size = (1200, 720)
    HospitalApp().run()




