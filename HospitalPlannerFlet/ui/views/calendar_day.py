from __future__ import annotations
import flet as ft
from datetime import datetime, timedelta, date

from ui.dialogs import snack

class CalendarDayView:
    def __init__(self, page: ft.Page, db, state, on_pick_slot: callable):
        self.page = page
        self.db = db
        self.state = state
        self.on_pick_slot = on_pick_slot
        self.view = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)

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

    def refresh(self):
        self.view.controls.clear()
        self.view.controls.append(ft.Text("Calendario diario", size=22, weight=ft.FontWeight.BOLD))

        # Header
        self.view.controls.append(
            ft.Row(
                [
                    ft.Text(f"Fecha: {self.state.calendar_date.isoformat()}", size=14),
                    ft.ElevatedButton("Cambiar fecha", on_click=self.open_date_picker),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )
        )

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
            slot_rows.append(
                ft.Container(
                    height=28,
                    ink=True,
                    on_click=lambda e, mm=m: on_slot_click(mm),
                    content=ft.Row(
                        [
                            ft.Container(width=70, content=ft.Text(label)),
                            ft.Container(expand=True, height=1, bgcolor=ft.Colors.GREY_200),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                    ),
                )
            )

        self.view.controls.append(
            ft.Container(
                border=ft.border.all(1, ft.Colors.GREY_300),
                border_radius=10,
                padding=10,
                content=ft.Column(slot_rows, spacing=0, scroll=ft.ScrollMode.AUTO, height=520),
            )
        )
        self.page.update()