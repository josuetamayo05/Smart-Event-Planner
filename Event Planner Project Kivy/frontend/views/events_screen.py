from __future__ import annotations
from kivy.properties import StringProperty
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard

class EventCard(MDCard):
    tittle= StringProperty("")
    subtitle = StringProperty("")

class EventsScreen(MDScreen):
    search_query=StringProperty("")

    @property
    def app(self):
        from kivy.app import App
        return App.get_running_app()

    def on_pre_enter(self, *args):
        self.refresh_events()

    def on_search_text(self, text:str):
        self.search_query=text
        self.refresh_events()

    def refresh_events(self):
        from backend.models.event import Event
        events=[Event.from_dict(e) for e in self.app.db.list_events()]
        q=(self.search_query or "").lower()
        if q:
            events=[e for e in events if q in e.name.lower() or q in e.event_type.lower()]

        events.sort(key=lambda e: e.start)
        rv=self.ids.events_rv
        rv.data=[
            {
                "tittle": e.name,
                "subtittle": f"{e.start.strftime('%Y-%m-%d %H:%M')} - {e.end.strftime('%H:%M')}",
            }
            for e in events
        ]
