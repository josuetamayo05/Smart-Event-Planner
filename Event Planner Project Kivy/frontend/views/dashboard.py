from __future__ import annotations
from datetime import date
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import OneLineListItem
from backend.models.event import Event

class DashboardScreen(MDScreen):
    @property
    def app(self):
        from kivy.app import App
        return App.get_running_app()

    def on_pre_enter(self, *args):
        self.refresh_today_events()

    def refresh_today_events(self):
        today = date.today()
        lst=self.ids.today_events_list
        lst.clear_widgets()
        events=[]
        for e_dict in self.app.db.list_events():
            ev=Event.from_dict(e_dict)
            if ev.start.date()==today:
                events.append(ev)
        events.sort(key=lambda x: x.start)
        for ev in events:
            item=OneLineListItem(
                text=f"{ev.start.strftime('%H:%M')} {ev.name}",
            )
            lst.add_widget(item)
    def on_tab_switch(self,instance_tabs, instance_tab, instance_tab_label,tab_text):
        #  cambiar entre vistas Día/Semana/Mes
        pass