from __future__ import annotations
import flet as ft
from ui.design import prime_color, dark_color, white_color, light_color

class DashboardView:
    def __init__(self, db):
        self.db = db
        self.view = ft.Column(spacing=14, scroll=ft.ScrollMode.AUTO)

    def _stat_card(self, title: str, value: int):
        return ft.Container(
            width=170,
            padding=16,
            border_radius=16,
            bgcolor=white_color,
            border=ft.border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.BLACK)),
            content=ft.Column(
                [
                    ft.Text(title, size=12, color=ft.Colors.with_opacity(0.75, ft.Colors.BLACK)),
                    ft.Text(str(value), size=26, weight=ft.FontWeight.BOLD, color=prime_color),
                ],
                spacing=6,
            ),
        )

    def refresh(self):
        self.view.controls.clear()
        events = self.db.list_events()
        resources = self.db.list_resources()

        # Header
        self.view.controls.append(
            ft.Text("Dashboard", size=28, weight=ft.FontWeight.BOLD, color=prime_color)
        )

        # Stats
        self.view.controls.append(
            ft.Row(
                [
                    self._stat_card("Eventos", len(events)),
                    self._stat_card("Recursos", len(resources)),
                ],
                spacing=14,
            )
        )

        # Próximos eventos (panel)
        self.view.controls.append(ft.Text("Próximos eventos:", size=16, weight=ft.FontWeight.W_600))

        if not events:
            self.view.controls.append(
                ft.Container(
                    padding=14,
                    border_radius=14,
                    bgcolor=light_color,
                    content=ft.Text("No hay eventos guardados.", color=ft.Colors.GREY_700),
                )
            )
            return

        events_sorted = sorted(events, key=lambda x: x.get("start", ""))[:12]

        lv = ft.ListView(spacing=6, padding=0, expand=False)
        for e in events_sorted:
            lv.controls.append(
                ft.Container(
                    padding=10,
                    border_radius=12,
                    bgcolor=light_color,
                    content=ft.Row(
                        [
                            ft.Container(
                                width=8, height=8,
                                border_radius=8,
                                bgcolor=dark_color
                            ),
                            ft.Text(
                                f"{e.get('start')} | {e.get('name')} ({e.get('event_type','')})",
                                size=12,
                            ),
                        ],
                        spacing=10,
                    ),
                )
            )

        self.view.controls.append(
            ft.Container(
                padding=14,
                border_radius=16,
                bgcolor=white_color,
                content=lv,
            )
        )