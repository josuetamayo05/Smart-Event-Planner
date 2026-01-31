from __future__ import annotations
import flet as ft
from uuid import uuid4

from ui.dialogs import snack, open_dialog, close_dialog, show_dialog
from ui.time_utils import parse_dt
from ui.design import *
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

        # UI helpers 
        def card(content, padding=16, radius=18):
            return ft.Container(
                padding=padding,
                border_radius=radius,
                bgcolor=ft.Colors.WHITE,
                border=ft.border.all(1, ft.Colors.GREY_200),
                shadow=[
                    ft.BoxShadow(
                        blur_radius=22,
                        spread_radius=1,
                        color=ft.Colors.BLACK12,
                        offset=ft.Offset(0, 10),
                    )
                ],
                content=content,
            )

        def pill(text: str, icon):
            return ft.Container(
                padding=ft.padding.symmetric(horizontal=12, vertical=8),
                border_radius=999,
                bgcolor=white_color,
                border=ft.border.all(1, ft.Colors.GREY_200),
                content=ft.Row(
                    spacing=8,
                    tight=True,
                    controls=[
                        ft.Icon(icon, size=18, color=sec_color),
                        ft.Text(text, size=13, weight=ft.FontWeight.BOLD, color=text_on_light),
                    ],
                ),
            )

        # Header moderno (gradiente)
        header = ft.Container(
            padding=18,
            border_radius=22,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=[prime_color, sec_color],
            ),
            shadow=[ft.BoxShadow(blur_radius=22, color=ft.Colors.BLACK12, offset=ft.Offset(0, 10))],
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                width=44,
                                height=44,
                                border_radius=16,
                                bgcolor=ft.Colors.WHITE,
                                alignment=ft.Alignment(0, 0),
                                content=ft.Icon(ft.Icons.EVENT_NOTE_OUTLINED, color=prime_color, size=22),
                            ),
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text("Eventos", size=22, weight=ft.FontWeight.BOLD, color="white"),
                                    ft.Text("Edita horarios y asignación de recursos", size=13, color=ft.Colors.WHITE),
                                ],
                            ),
                        ],
                    ),
                    ft.Container(
                        padding=10,
                        border_radius=16,
                        bgcolor=ft.Colors.WHITE,
                        content=ft.Icon(ft.Icons.CALENDAR_MONTH_OUTLINED, color=prime_color, size=22),
                    ),
                ],
            ),
        )
        self.view.controls.append(header)

        events = sorted(self.db.list_events(), key=lambda x: x.get("start", ""))

        # Empty state 
        if not events:
            self.view.controls.append(
                card(
                    ft.Column(
                        spacing=8,
                        controls=[
                            ft.Row(
                                spacing=10,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Icon(ft.Icons.INFO_OUTLINE, color=sec_color),
                                    ft.Text("No hay eventos.", size=14, color=text_on_light, weight=ft.FontWeight.BOLD),
                                ],
                            ),
                            ft.Text(
                                "Cuando existan eventos, aquí podrás editarlos y gestionar conflictos.",
                                size=12,
                                color=ft.Colors.GREY_700,
                            ),
                        ],
                    ),
                    padding=16,
                    radius=18,
                )
            )
            return

        # Barra de info arriba
        info_bar = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                pill(f"Total: {len(events)}", ft.Icons.LIST_ALT),
                pill("Tip: usa ✏️ para editar", ft.Icons.TIPS_AND_UPDATES_OUTLINED),
            ],
        )
        self.view.controls.append(card(info_bar, padding=14, radius=18))

        table = ft.DataTable(
            column_spacing=18,
            horizontal_margin=12,
            divider_thickness=0.6,
            heading_row_height=46,
            data_row_min_height=46,
            data_row_max_height=56,
            columns=[
                ft.DataColumn(ft.Text("Inicio", weight=ft.FontWeight.BOLD, color=text_on_light)),
                ft.DataColumn(ft.Text("Fin", weight=ft.FontWeight.BOLD, color=text_on_light)),
                ft.DataColumn(ft.Text("Nombre", weight=ft.FontWeight.BOLD, color=text_on_light)),
                ft.DataColumn(ft.Text("Tipo", weight=ft.FontWeight.BOLD, color=text_on_light)),
                ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD, color=text_on_light)),
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
                bgcolor=ft.Colors.WHITE,
                title=ft.Row(
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            width=38,
                            height=38,
                            border_radius=14,
                            bgcolor=white_color,
                            border=ft.border.all(1, ft.Colors.GREY_200),
                            alignment=ft.Alignment(0, 0),
                            content=ft.Icon(ft.Icons.EDIT_CALENDAR_OUTLINED, color=prime_color, size=20),
                        ),
                        ft.Text("Editar evento", size=18, weight=ft.FontWeight.BOLD, color=text_on_light),
                    ],
                ),
                content=ft.Container(
                    width=560,
                    padding=16,
                    border_radius=18,
                    bgcolor=white_color,
                    border=ft.border.all(1, ft.Colors.GREY_200),
                    content=ft.Column(
                        [
                            name_edit, type_edit,
                            ft.Row([date_edit, start_edit, end_edit]),
                            ft.Text("Recursos", weight=ft.FontWeight.BOLD, color=text_on_light),
                            ft.Container(
                                res_col,
                                border=ft.border.all(1, ft.Colors.GREY_300),
                                border_radius=14,
                                padding=10,
                                height=180,
                                bgcolor=ft.Colors.WHITE,
                            ),
                        ],
                        tight=True, scroll=ft.ScrollMode.AUTO, height=520
                    ),
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
                ft.ElevatedButton(
                    "Guardar cambios",
                    on_click=on_save,
                    bgcolor=prime_color,
                    color="white",
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=14),
                        padding=ft.padding.symmetric(horizontal=18, vertical=12),
                    ),
                ),
            ]
            open_dialog(self.page, dlg)

        for e in events:
            table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(e.get("start", ""), color=text_on_light)),
                        ft.DataCell(ft.Text(e.get("end", ""), color=text_on_light)),
                        ft.DataCell(ft.Text(e.get("name", ""), color=text_on_light)),
                        ft.DataCell(ft.Text(e.get("event_type", ""), color=text_on_light)),
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.IconButton(
                                        icon=ft.Icons.EDIT,
                                        tooltip="Editar",
                                        icon_color=sec_color,
                                        on_click=lambda ev, _e=e: open_event_dialog(_e)
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE,
                                        tooltip="Eliminar",
                                        icon_color=ft.Colors.RED_400,
                                        on_click=lambda ev, _id=e["id"]: delete_event(_id)
                                    ),
                                ],
                                spacing=0,
                            )
                        ),
                    ]
                )
            )

        # Tabla dentro de contenedor 
        self.view.controls.append(
            ft.Container(
                padding=12,
                border_radius=18,
                bgcolor=ft.Colors.WHITE,
                border=ft.border.all(1, ft.Colors.GREY_200),
                shadow=[
                    ft.BoxShadow(
                        blur_radius=22,
                        spread_radius=1,
                        color=ft.Colors.BLACK12,
                        offset=ft.Offset(0, 10),
                    )
                ],
                content=table,
            )
        )