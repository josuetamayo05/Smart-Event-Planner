from __future__ import annotations
import flet as ft

class DashboardView:
    def __init__(self,db):
        self.db=db
        self.view=ft.Column(spacing=10,scroll=ft.ScrollMode.AUTO)

    def refresh(self):
        self.view.controls.clear()
        events=self.db.list_events()
        resources=self.db.list_resources()

        self.view.controls.append(ft.Text("Dashboard", size=22, weight=ft.FontWeight.BOLD))
        self.view.controls.append(
            ft.Row([
                ft.Card(ft.Container(ft.Column([ft.Text("Eventos"), ft.Text(str(len(events)), size=20)]), padding=12)),
                ft.Card(ft.Container(ft.Column([ft.Text("Recursos"), ft.Text(str(len(resources)), size=20)]), padding=12)),
            ])
        )

        self.view.controls.append(ft.Text("Próximos eventos:", size=16))
        if not events:
            self.view.controls.append(ft.Text("No hay eventos guardados."))
        else:
            for e in sorted(events, key=lambda x: x.get("start", ""))[:10]:
                self.view.controls.append(ft.Text(f"- {e.get('start')} | {e.get('name')} ({e.get('event_type','')})"))