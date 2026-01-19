from datetime import date

from kivy.clock import Clock
from kivymd.uix.screen import MDScreen
# from kivymd.uix.list import OneLineListItem

# try:
#     from backend.models.event import Event
# except Exception:
#     Event = None

class DashboardScreen(MDScreen):
    pass
    # def on_pre_enter(self, *args):
    #     # Espera a que el KV termine de construir ids
    #     Clock.schedule_once(lambda dt: self.refresh_today_events(), 0)
    #
    # def refresh_today_events(self):
    #     if "today_events" not in self.ids:
    #         return
    #
    #     today = date.today()
    #     lst=self.ids.today_events_list
    #     lst.clear_widgets()
    #     events=[]
    #
    #     for e_dict in self.app.db.list_events():
    #         ev=Event.from_dict(e_dict)
    #         if ev.start.date()==today:
    #             events.append(ev)
    #
    #     events.sort(key=lambda x: x.start)
    #
    #     if not events:
    #         lst.add_widget(OneLineListItem(text="No hay eventos hoy."))
    #         return
    #
    #     for ev in events:
    #         lst.add_widget(OneLineListItem(text=f"{ev.start.strftime('%H:%M')} {ev.name}"))
    #
    # def get_running_app(self):
    #     from kivy.app import App
    #     return App.get_running_app()