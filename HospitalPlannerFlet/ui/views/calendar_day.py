from __future__ import annotations
import flet as ft
from datetime import datetime, timedelta, date

from ui.design import *
from ui.dialogs import snack

class CalendarDayView:
    def __init__(self, page: ft.Page, db, state, on_pick_slot: callable):
        self.page = page
        self.db = db
        self.state = state
        self.on_pick_slot = on_pick_slot

        # Contenedor principal del view 
        self.view = ft.Column(
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
        )

        self.date_picker = ft.DatePicker(
            first_date=datetime(2020, 1, 1),
            last_date=datetime(2035, 12, 31),
            value=datetime.now(),
        )
        self.date_picker.on_change = self._on_pick_date
        self.page.overlay.append(self.date_picker)

    def _on_pick_date(self, e):
        if self.date_picker.value:
            self.state.calendar_date = self.date_picker.value.date()
            self.refresh()

    def open_date_picker(self, _):
        self.date_picker.open = True
        self.page.update()

    # UI helpers 
    def _glass_card(self, content: ft.Control, *, padding=16, radius=18):
        return ft.Container(
            padding=padding,
            border_radius=radius,
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, ft.Colors.with_opacity(0.14, sec_color)),
            shadow=[
                ft.BoxShadow(
                    blur_radius=22,
                    spread_radius=1,
                    color=ft.Colors.with_opacity(0.10, "#0B1220"),
                    offset=ft.Offset(0, 10),
                )
            ],
            content=content,
        )

    def _pill(self, text: str, icon_name: str):
        return ft.Container(
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
            border_radius=999,
            bgcolor=ft.Colors.with_opacity(0.12, prime_color),
            border=ft.border.all(1, ft.Colors.with_opacity(0.18, prime_color)),
            content=ft.Row(
                spacing=8,
                tight=True,
                controls=[
                    ft.Icon(icon_name, size=18, color=prime_color),
                    ft.Text(text, size=13, weight=ft.FontWeight.W_600, color=text_on_light),
                ],
            ),
        )

    def refresh(self):
        self.view.controls.clear()

        # Header superior 
        header = ft.Container(
            padding=18,
            border_radius=22,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=[
                    prime_color,
                    sec_color,
                ],
            ),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(
                                "Calendario diario",
                                size=22,
                                weight=ft.FontWeight.W_800,
                                color="white",
                            ),
                            ft.Text(
                                "Selecciona un horario disponible",
                                size=13,
                                color=ft.Colors.with_opacity(0.9, "white"),
                            ),
                        ],
                    ),
                    ft.Container(
                        padding=10,
                        border_radius=16,
                        bgcolor=ft.Colors.with_opacity(0.18, "white"),
                        border=ft.border.all(1, ft.Colors.with_opacity(0.20, "white")),
                        content=ft.Icon(ft.Icons.CALENDAR_MONTH_OUTLINED, color="white", size=22),
                    ),
                ],
            ),
        )
        self.view.controls.append(header)

        # Barra de fecha + botón
        date_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self._pill(f"Fecha: {self.state.calendar_date.isoformat()}", ft.Icons.EVENT),
                ft.ElevatedButton(
                    "Cambiar fecha",
                    on_click=self.open_date_picker,
                    bgcolor=prime_color,
                    color="white",
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=14),
                        padding=ft.padding.symmetric(horizontal=18, vertical=12),
                    ),
                ),
            ],
        )
        self.view.controls.append(self._glass_card(date_row, padding=14, radius=18))

        # Slots clickeables 
        DAY_START = 7
        DAY_END = 20
        SLOT_MIN = 15

        def on_slot_click(minutes_of_day: int):
            start_h, start_m = divmod(minutes_of_day, 60)
            end_minutes = min(DAY_END * 60, minutes_of_day + 60)
            end_h, end_m = divmod(end_minutes, 60)

            self.on_pick_slot(
                self.state.calendar_date.isoformat(),
                f"{start_h:02d}:{start_m:02d}",
                f"{end_h:02d}:{end_m:02d}",
            )

        slot_rows = []
        for m in range(DAY_START * 60, DAY_END * 60, SLOT_MIN):
            label = f"{m//60:02d}:00" if m % 60 == 0 else ""

            #  marca suavemente las horas en punto
            is_full_hour = (m % 60 == 0)
            row_bg = ft.Colors.with_opacity(0.45, white_color) if is_full_hour else ft.Colors.with_opacity(0.20, white_color)

            slot_rows.append(
                ft.Container(
                    height=34,
                    border_radius=14,
                    padding=ft.padding.symmetric(horizontal=10),
                    bgcolor=row_bg,
                    ink=True,
                    on_click=lambda e, mm=m: on_slot_click(mm),
                    content=ft.Row(
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                width=76,
                                content=ft.Text(
                                    label,
                                    size=12,
                                    weight=ft.FontWeight.W_700 if is_full_hour else ft.FontWeight.W_500,
                                    color=sec_color if label else ft.Colors.with_opacity(0.65, text_on_light),
                                ),
                            ),
                            ft.Container(
                                expand=True,
                                height=1,
                                bgcolor=ft.Colors.with_opacity(0.18, sec_color),
                            ),
                            ft.Icon(
                                ft.Icons.CHEVRON_RIGHT,
                                size=18,
                                color=ft.Colors.with_opacity(0.50, text_on_light),
                            ),
                        ],
                    ),
                )
            )

        slots_card = self._glass_card(
            ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text(
                                "Horarios",
                                size=16,
                                weight=ft.FontWeight.W_700,
                                color=text_on_light,
                            ),
                            ft.Container(
                                padding=ft.padding.symmetric(horizontal=10, vertical=6),
                                border_radius=999,
                                bgcolor=ft.Colors.with_opacity(0.10, dark_color),
                                border=ft.border.all(1, ft.Colors.with_opacity(0.16, dark_color)),
                                content=ft.Text(
                                    f"{DAY_START:02d}:00–{DAY_END:02d}:00",
                                    size=12,
                                    weight=ft.FontWeight.W_600,
                                    color=text_on_light,
                                ),
                            ),
                        ],
                    ),
                    ft.Container(
                        border_radius=16,
                        bgcolor=ft.Colors.with_opacity(0.35, white_color),
                        border=ft.border.all(1, ft.Colors.with_opacity(0.12, sec_color)),
                        padding=10,
                        content=ft.Column(
                            slot_rows,
                            spacing=8,
                            scroll=ft.ScrollMode.AUTO,
                            height=520,
                        ),
                    ),
                ],
            ),
            padding=16,
            radius=18,
        )

        self.view.controls.append(slots_card)

        self.page.update()