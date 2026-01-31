from __future__ import annotations
import flet as ft
from ui.design import prime_color, dark_color, white_color, light_color

class DashboardView:
    def __init__(self, db):
        self.db = db
        self.view = ft.Column(expand=True,spacing=14, scroll=ft.ScrollMode.AUTO)

    def _stat_card(self, title: str, value: int):
        # Tarjeta estadística 
        icon_map = {
            "Eventos": ft.Icons.EVENT_NOTE_OUTLINED,
            "Recursos": ft.Icons.INVENTORY_2_OUTLINED,
        }
        icon = icon_map.get(title, ft.Icons.INSIGHTS_OUTLINED)

        return ft.Container(
            width=200,
            padding=16,
            border_radius=18,
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, ft.Colors.with_opacity(0.10, ft.Colors.BLACK)),
            shadow=[
                ft.BoxShadow(
                    blur_radius=22,
                    spread_radius=1,
                    color=ft.Colors.BLACK12,
                    offset=ft.Offset(0, 10),
                )
            ],
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Column(
                        spacing=4,
                        controls=[
                            ft.Text(
                                title,
                                size=12,
                                color=ft.Colors.with_opacity(0.70, ft.Colors.BLACK),
                                weight=ft.FontWeight.W_600,
                            ),
                            ft.Text(
                                str(value),
                                size=28,
                                weight=ft.FontWeight.BOLD,
                                color=prime_color,
                            ),
                        ],
                    ),
                    ft.Container(
                        width=44,
                        height=44,
                        border_radius=16,
                        bgcolor=ft.Colors.with_opacity(0.14, prime_color),
                        border=ft.border.all(1, ft.Colors.with_opacity(0.18, prime_color)),
                        alignment=ft.Alignment(0, 0),
                        content=ft.Icon(icon, color=prime_color, size=22),
                    ),
                ],
            ),
        )

    def refresh(self):
        self.view.controls.clear()
        events = self.db.list_events()
        resources = self.db.list_resources()

        # Header
        self.view.controls.append(
            ft.Container(
                padding=18,
                border_radius=22,
                gradient=ft.LinearGradient(
                    begin=ft.Alignment(-1, -1),
                    end=ft.Alignment(1, 1),
                    colors=[prime_color, dark_color],
                ),
                shadow=[
                    ft.BoxShadow(
                        blur_radius=22,
                        spread_radius=1,
                        color=ft.Colors.BLACK12,
                        offset=ft.Offset(0, 10),
                    )
                ],
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            spacing=2,
                            controls=[
                                ft.Text("Dashboard", size=26, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                ft.Text(
                                    "Resumen rápido del día",
                                    size=13,
                                    color=ft.Colors.with_opacity(0.92, ft.Colors.WHITE),
                                ),
                            ],
                        ),
                        ft.Container(
                            padding=10,
                            border_radius=16,
                            bgcolor=ft.Colors.with_opacity(0.18, ft.Colors.WHITE),
                            border=ft.border.all(1, ft.Colors.with_opacity(0.22, ft.Colors.WHITE)),
                            content=ft.Icon(ft.Icons.DASHBOARD_OUTLINED, color=ft.Colors.WHITE, size=22),
                        ),
                    ],
                ),
            )
        )

        # Stats
        self.view.controls.append(
            ft.Row(
                [
                    self._stat_card("Eventos", len(events)),
                    self._stat_card("Recursos", len(resources)),
                ],
                spacing=14,
                wrap=True,
            )
        )

        # Próximos eventos (panel)
        self.view.controls.append(
            ft.Row(
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=34,
                        height=34,
                        border_radius=14,
                        bgcolor=ft.Colors.with_opacity(0.14, dark_color),
                        border=ft.border.all(1, ft.Colors.with_opacity(0.18, dark_color)),
                        alignment=ft.Alignment(0, 0),
                        content=ft.Icon(ft.Icons.SCHEDULE, color=dark_color, size=18),
                    ),
                    ft.Text("Próximos eventos:", size=16, weight=ft.FontWeight.W_700, color=ft.Colors.BLACK),
                ],
            )
        )

        if not events:
            self.view.controls.append(
                ft.Container(
                    padding=16,
                    border_radius=18,
                    bgcolor=ft.Colors.WHITE,
                    border=ft.border.all(1, ft.Colors.with_opacity(0.10, ft.Colors.BLACK)),
                    shadow=[
                        ft.BoxShadow(
                            blur_radius=18,
                            spread_radius=1,
                            color=ft.Colors.BLACK12,
                            offset=ft.Offset(0, 8),
                        )
                    ],
                    content=ft.Row(
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(ft.Icons.INFO_OUTLINE, color=prime_color),
                            ft.Text("No hay eventos guardados.", color=ft.Colors.GREY_700),
                        ],
                    ),
                )
            )
            return

        events_sorted = sorted(events, key=lambda x: x.get("start", ""))[:12]

        lv = ft.ListView(spacing=8, padding=0, expand=False)
        for e in events_sorted:
            lv.controls.append(
                ft.Container(
                    padding=12,
                    border_radius=16,
                    bgcolor=ft.Colors.with_opacity(0.55, white_color),
                    border=ft.border.all(1, ft.Colors.with_opacity(0.10, ft.Colors.BLACK)),
                    content=ft.Row(
                        [
                            ft.Container(
                                width=10,
                                height=10,
                                border_radius=10,
                                bgcolor=dark_color
                            ),
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(
                                        f"{e.get('start')} → {e.get('end')}",
                                        size=12,
                                        color=ft.Colors.with_opacity(0.75, ft.Colors.BLACK),
                                        weight=ft.FontWeight.W_600,
                                    ),
                                    ft.Text(
                                        f"{e.get('name')} ({e.get('event_type','')})",
                                        size=12,
                                        color=ft.Colors.BLACK,
                                    ),
                                ],
                            ),
                        ],
                        spacing=10,
                    ),
                )
            )

        self.view.controls.append(
            ft.Container(
                padding=14,
                border_radius=18,
                bgcolor=ft.Colors.WHITE,
                border=ft.border.all(1, ft.Colors.with_opacity(0.10, ft.Colors.BLACK)),
                shadow=[
                    ft.BoxShadow(
                        blur_radius=18,
                        spread_radius=1,
                        color=ft.Colors.BLACK12,
                        offset=ft.Offset(0, 8),
                    )
                ],
                content=lv,
            )
        )