import flet as ft

from models.database_manager import DatabaseManager
from models.scheduler import Scheduler

from ui.state import AppState
from ui.views.dashboard import DashboardView
from ui.views.events import EventsView
from ui.views.resources import ResourcesView
from ui.views.new_event import NewEventView
from ui.views.calendar_day import CalendarDayView


def main(page: ft.Page):
    page.title = "Planificador hospitalario"
    try:
        page.window.width = 1200
        page.window.height = 720
    except Exception:
        pass

    db = DatabaseManager("database.json")
    scheduler = Scheduler(db)
    state = AppState()

    content = ft.Container(expand=True, padding=15)

    # callback global cuando cambia algo (para refrescar dashboard etc.)
    def on_any_change():
        dashboard.refresh()
        events.refresh()
        # no refrescamos recursos siempre, pero podrías hacerlo si quieres
        page.update()

    dashboard = DashboardView(db)
    events = EventsView(page, db, scheduler, on_any_change)
    resources = ResourcesView(page, db)

    # new event necesita state porque usa selected_resource_ids
    new_event = NewEventView(page, db, scheduler, state, on_any_change)

    def pick_slot_from_calendar(date_iso: str, start_hhmm: str, end_hhmm: str):
        new_event.set_times(date_iso, start_hhmm, end_hhmm)
        state.selected_index = 2
        render()

    calendar = CalendarDayView(page, db, state, on_pick_slot=pick_slot_from_calendar)

    def render():
        idx = state.selected_index
        nav.selected_index = idx

        if idx == 0:
            dashboard.refresh()
            content.content = dashboard.view
        elif idx == 1:
            events.refresh()
            content.content = events.view
        elif idx == 2:
            new_event.build_resources_checklist()
            new_event.quick_validate()
            content.content = new_event.view
        elif idx == 3:
            calendar.refresh()
            content.content = calendar.view
        elif idx == 4:
            resources.refresh()
            content.content = resources.view

        page.update()

    def go_to(i: int):
        state.selected_index = i
        render()

    nav = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        destinations=[
            ft.NavigationRailDestination(icon=ft.Icons.DASHBOARD, label="Dashboard"),
            ft.NavigationRailDestination(icon=ft.Icons.EVENT, label="Eventos"),
            ft.NavigationRailDestination(icon=ft.Icons.ADD_BOX, label="Nuevo evento"),
            ft.NavigationRailDestination(icon=ft.Icons.CALENDAR_MONTH, label="Calendario"),
            ft.NavigationRailDestination(icon=ft.Icons.MEDICAL_SERVICES, label="Recursos"),
        ],
        on_change=lambda e: go_to(e.control.selected_index),
    )

    page.add(ft.Row([nav, ft.VerticalDivider(width=1), content], expand=True))
    render()


if __name__ == "__main__":
    ft.run(main)