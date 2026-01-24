import flet as ft

from ui.design import prime_color, sec_color, light_color, dark_color, white_color, text_on_dark, text_on_light
from ui.state import AppState

from models.database_manager import DatabaseManager
from models.scheduler import Scheduler

from ui.views.dashboard import DashboardView
from ui.views.events import EventsView
from ui.views.resources import ResourcesView
from ui.views.new_event import NewEventView
from ui.views.calendar_day import CalendarDayView


def main(page: ft.Page):
    page.title = "Planificador hospitalario"
    page.window_width = 1000
    page.window_height = 600
    page.padding = 0
    page.window_resizable = False
    page.window_maximizable = False 
    page.padding = 0

    db = DatabaseManager("database.json")
    scheduler = Scheduler(db)
    state = AppState()

    # Views
    def on_any_change():
        dashboard.refresh()
        events.refresh()
        page.update()

    dashboard = DashboardView(db)
    events = EventsView(page, db, scheduler, on_any_change)
    resources = ResourcesView(page, db)
    new_event = NewEventView(page, db, scheduler, state, on_any_change)

    def pick_slot_from_calendar(date_iso: str, start_hhmm: str, end_hhmm: str):
        new_event.set_times(date_iso, start_hhmm, end_hhmm)
        show_screen(2)

    calendar = CalendarDayView(page, db, state, on_pick_slot=pick_slot_from_calendar)

    # Right container (content area)
    right_container = ft.Container(
        bgcolor=white_color,
        expand=9,
        padding=18,
        border_radius=14,
    )

    # Header top bar
    header = ft.Container(
        height=64,
        bgcolor=prime_color,
        alignment=ft.alignment.Alignment(0, 0),
        content=ft.Text(
            "PLANIFICADOR HOSPITALARIO",
            color=text_on_dark,
            size=24,
            weight=ft.FontWeight.W_700,
        ),
    )

    # Helper: item visual (seleccionado vs normal)
    def nav_item(text: str, icon, idx: int):
        selected = (state.selected_index == idx)
        return ft.Container(
            border_radius=14,
            bgcolor=dark_color if selected else ft.Colors.TRANSPARENT,
            padding=ft.padding.symmetric(horizontal=10, vertical=10),
            on_click=lambda e: show_screen(idx),
            content=ft.Row(
                [
                    ft.Icon(icon, color=(text_on_dark if selected else prime_color)),
                    ft.Text(text, color=(text_on_dark if selected else prime_color), weight=ft.FontWeight.W_600),
                ],
                spacing=10,
            ),
        )

    left_col = ft.Column(
        [
            ft.Container(
                alignment=ft.alignment.Alignment(0,0),
                content=ft.Icon(ft.Icons.LOCAL_HOSPITAL, color=prime_color, size=48),
            ),
            ft.Divider(height=8, color=ft.Colors.TRANSPARENT),

            nav_item("Dashboard", ft.Icons.DASHBOARD, 0),
            nav_item("Eventos", ft.Icons.EVENT, 1),
            nav_item("Nuevo evento", ft.Icons.ADD, 2),
            nav_item("Calendario", ft.Icons.CALENDAR_MONTH, 3),
            nav_item("Recursos", ft.Icons.MEDICAL_SERVICES, 4),

            ft.Container(expand=True),
            ft.Text("Versión 1.0", size=10, color=prime_color),
        ],
        spacing=10,
    )

    left_container = ft.Container(
        bgcolor=light_color,
        expand=2,
        content=left_col,
        padding=14,
        border_radius=14,
    )

    def show_screen(idx: int):
        state.selected_index = idx

        if idx == 0:
            dashboard.refresh()
            right_container.content = dashboard.view
        elif idx == 1:
            events.refresh()
            right_container.content = events.view
        elif idx == 2:
            new_event.build_resources_checklist()
            new_event.quick_validate()
            right_container.content = new_event.view
        elif idx == 3:
            calendar.refresh()
            right_container.content = calendar.view
        elif idx == 4:
            resources.refresh()
            right_container.content = resources.view

        # refrescar sidebar (para resaltar item seleccionado)
        left_container.content = left_col
        page.update()

    main_row = ft.Row(
        [left_container, ft.VerticalDivider(width=1), right_container],
        spacing=0,
        expand=True,
    )

    page.add(
        ft.Container(
            bgcolor=sec_color,
            expand=True,
            content=ft.Column([header, ft.Divider(height=1), main_row], spacing=0),
        )
    )

    show_screen(0)


if __name__ == "__main__":
    ft.run(main)