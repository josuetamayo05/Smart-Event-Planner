from __future__ import annotations
import flet as ft
from uuid import uuid4

from ui.dialogs import snack, open_dialog, close_dialog, show_dialog
from ui.time_utils import parse_dt
from models.event import Event

class EventsView:
    def __init__(self, page: ft.Page, db, scheduler, on_any_change: callable):
        self.page = page
        self.db = db
        self.scheduler = scheduler
        self.on_any_change = on_any_change
        self.view = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)

    def refresh(self):
        self.view.controls.clear()
        self.view.controls.append(ft.Text("Eventos", size=22, weight=ft.FontWeight.BOLD))

        events = sorted(self.db.list_events(), key=lambda x: x.get("start", ""))
        if not events:
            self.view.controls.append(ft.Text("No hay eventos."))
            return

        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Inicio")),
                ft.DataColumn(ft.Text("Fin")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Tipo")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[],
        )

        def delete_event(event_id: str):
            self.db.delete_event(event_id)
            snack(self.page, "Evento eliminado.")
            self.on_any_change()
            self.refresh()
            self.page.update()

        def open_event_dialog(existing: dict):
            name_edit = ft.TextField(label="Nombre", value=existing.get("name", ""))
            type_edit = ft.TextField(label="Tipo", value=existing.get("event_type", ""))

            start_iso = existing.get("start", "")
            end_iso = existing.get("end", "")

            date_edit = ft.TextField(label="Fecha (YYYY-MM-DD)", value=start_iso.split("T")[0] if "T" in start_iso else "")
            start_edit = ft.TextField(label="Hora inicio (HH:MM)", value=start_iso.split("T")[1] if "T" in start_iso else "09:00")
            end_edit = ft.TextField(label="Hora fin (HH:MM)", value=end_iso.split("T")[1] if "T" in end_iso else "11:00")

            selected_ids = set(existing.get("resource_ids", []))
            res_col = ft.Column(spacing=2)

            def rebuild_checks():
                res_col.controls.clear()
                for r in self.db.list_resources():
                    rid = r["id"]
                    rname = r.get("name", rid)

                    def on_change(e, _rid=rid):
                        if e.control.value:
                            selected_ids.add(_rid)
                        else:
                            selected_ids.discard(_rid)

                    res_col.controls.append(ft.Checkbox(label=rname, value=(rid in selected_ids), on_change=on_change))

            rebuild_checks()

            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("Editar evento"),
                content=ft.Column(
                    [
                        name_edit, type_edit,
                        ft.Row([date_edit, start_edit, end_edit]),
                        ft.Text("Recursos"),
                        ft.Container(res_col, border=ft.border.all(1, ft.Colors.GREY_300), padding=10, height=180),
                    ],
                    tight=True, scroll=ft.ScrollMode.AUTO, height=520
                ),
                actions=[],
            )

            def on_save(_):
                if not name_edit.value.strip():
                    snack(self.page, "El nombre es obligatorio.")
                    return
                if not selected_ids:
                    snack(self.page, "Selecciona al menos un recurso.")
                    return
                try:
                    new_start = parse_dt(date_edit.value, start_edit.value)
                    new_end = parse_dt(date_edit.value, end_edit.value)
                except Exception:
                    snack(self.page, "Fecha/hora inválidas.")
                    return
                if new_end <= new_start:
                    snack(self.page, "Hora fin debe ser mayor que inicio.")
                    return

                ev = Event(
                    id=existing["id"],
                    name=name_edit.value.strip(),
                    description=existing.get("description", ""),
                    event_type=type_edit.value.strip(),
                    start=new_start,
                    end=new_end,
                    resource_ids=list(selected_ids),
                )
                violations = self.scheduler.validate_event(ev)
                if violations:
                    show_dialog(self.page, "Conflictos detectados", "\n".join(f"• {v.message}" for v in violations))
                    return

                self.db.upsert_event(ev.to_dict())
                close_dialog(self.page, dlg)
                snack(self.page, "Evento actualizado.")
                self.on_any_change()
                self.refresh()
                self.page.update()

            dlg.actions = [
                ft.TextButton("Cancelar", on_click=lambda e: close_dialog(self.page, dlg)),
                ft.ElevatedButton("Guardar cambios", on_click=on_save),
            ]
            open_dialog(self.page, dlg)

        for e in events:
            table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(e.get("start", ""))),
                        ft.DataCell(ft.Text(e.get("end", ""))),
                        ft.DataCell(ft.Text(e.get("name", ""))),
                        ft.DataCell(ft.Text(e.get("event_type", ""))),
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.IconButton(icon=ft.Icons.EDIT, tooltip="Editar",
                                                  on_click=lambda ev, _e=e: open_event_dialog(_e)),
                                    ft.IconButton(icon=ft.Icons.DELETE, tooltip="Eliminar",
                                                  on_click=lambda ev, _id=e["id"]: delete_event(_id)),
                                ],
                                spacing=0,
                            )
                        ),
                    ]
                )
            )

        self.view.controls.append(table)