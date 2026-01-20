from __future__ import annotations
import flet as ft
from datetime import date, timedelta
from uuid import uuid4

from ui.dialogs import snack, show_dialog
from ui.time_utils import parse_dt
from models.event import Event

class NewEventView:
    def __init__(self, page: ft.Page, db, scheduler, state, on_any_change: callable):
        self.page = page
        self.db = db
        self.scheduler = scheduler
        self.state = state
        self.on_any_change = on_any_change

        self.name_tf = ft.TextField(label="Nombre del evento")
        self.type_tf = ft.TextField(label="Tipo (ej. cirugia_cardiaca)")
        self.date_tf = ft.TextField(label="Fecha (YYYY-MM-DD)", value=str(date.today()))
        self.start_tf = ft.TextField(label="Hora inicio (HH:MM)", value="09:00")
        self.end_tf = ft.TextField(label="Hora fin (HH:MM)", value="11:00")

        self.duration_tf = ft.TextField(label="Duración (minutos)", value="120")
        self.slots_column = ft.Column(spacing=6)

        self.validation_text = ft.Text("")
        self.resources_column = ft.Column(spacing=2)

        for tf in (self.name_tf, self.type_tf, self.date_tf, self.start_tf, self.end_tf):
            tf.on_change = lambda e: self.quick_validate()

        self.view = ft.Column(
            [
                ft.Text("Nuevo evento", size=22, weight=ft.FontWeight.BOLD),
                self.name_tf,
                self.type_tf,
                ft.Row([self.date_tf, self.start_tf, self.end_tf]),
                self.validation_text,

                ft.Divider(),
                ft.Text("Recursos (elige el fijo, ej: OR1)", size=16),
                ft.Container(self.resources_column, border=ft.border.all(1, ft.Colors.GREY_300), padding=10),

                ft.Divider(),
                ft.Text("Búsqueda inteligente (autofill)", size=16, weight=ft.FontWeight.BOLD),
                self.duration_tf,
                ft.ElevatedButton("Buscar próximo horario disponible", on_click=self.on_find_slots),
                self.slots_column,

                ft.ElevatedButton("Guardar", on_click=self.on_save),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def set_times(self, date_iso: str, start_hhmm: str, end_hhmm: str):
        self.date_tf.value = date_iso
        self.start_tf.value = start_hhmm
        self.end_tf.value = end_hhmm

    def build_resources_checklist(self, preselected=None):
        preselected = set(preselected or [])
        self.resources_column.controls.clear()
        self.state.selected_resource_ids.clear()
        self.state.selected_resource_ids.update(preselected)

        for r in self.db.list_resources():
            rid = r["id"]
            rname = r.get("name", rid)

            def on_change(e, _rid=rid):
                if e.control.value:
                    self.state.selected_resource_ids.add(_rid)
                else:
                    self.state.selected_resource_ids.discard(_rid)
                self.quick_validate()

            self.resources_column.controls.append(
                ft.Checkbox(label=rname, value=(rid in preselected), on_change=on_change)
            )

    def quick_validate(self):
        self.validation_text.value = ""
        try:
            start_dt = parse_dt(self.date_tf.value, self.start_tf.value)
            end_dt = parse_dt(self.date_tf.value, self.end_tf.value)
        except Exception:
            self.validation_text.value = "Completa fecha/hora válidas (YYYY-MM-DD y HH:MM)."
            self.validation_text.color = ft.Colors.RED
            self.page.update()
            return
        
        if start_dt>=end_dt:
            self.validation_text.value = "Hora fin debe ser posterior a inicio siempre."
            self.validation_text.color = ft.Colors.RED
            self.page.update()
            return

        temp = Event(
            id="__tmp__",
            name=self.name_tf.value.strip() or "Evento",
            description="",
            event_type=self.type_tf.value.strip(),
            start=start_dt,
            end=end_dt,
            resource_ids=list(self.state.selected_resource_ids),
        )
        violations = self.scheduler.validate_event(temp)
        if violations:
            self.validation_text.value = violations[0].message
            self.validation_text.color = ft.Colors.RED
        else:
            self.validation_text.value = "Sin conflictos detectados."
            self.validation_text.color = ft.Colors.GREEN

        self.page.update()

    def on_find_slots(self, _):
        self.slots_column.controls.clear()

        fixed_ids = list(self.state.selected_resource_ids)
        if not fixed_ids:
            self.slots_column.controls.append(ft.Text("Selecciona primero el recurso fijo (ej: OR1) y vuelve a buscar."))
            self.page.update()
            return

        try:
            from_dt = parse_dt(self.date_tf.value, self.start_tf.value)
        except Exception:
            snack(self.page, "Fecha/hora inválidas para iniciar la búsqueda.")
            return

        try:
            mins = int((self.duration_tf.value or "").strip())
            duration = timedelta(minutes=mins)
        except Exception:
            snack(self.page, "Duración inválida (minutos).")
            return

        event_type = (self.type_tf.value or "").strip()
        results = self.scheduler.find_next_slots_autofill(
            fixed_resource_ids=fixed_ids,
            event_type=event_type,
            duration=duration,
            from_dt=from_dt,
            max_results=3,
        )

        if not results:
            self.slots_column.controls.append(ft.Text("No se encontraron horarios disponibles con esos recursos."))
            self.page.update()
            return

        def use_slot(slot):
            self.date_tf.value = slot.start.strftime("%Y-%m-%d")
            self.start_tf.value = slot.start.strftime("%H:%M")
            self.end_tf.value = slot.end.strftime("%H:%M")

            pre = [r.id for r in slot.resources]
            self.build_resources_checklist(preselected=pre)
            self.quick_validate()
            self.page.update()
            snack(self.page, "Horario y recursos aplicados al formulario.")

        for slot in results:
            res_names = ", ".join(r.name for r in slot.resources)
            self.slots_column.controls.append(
                ft.Card(
                    ft.Container(
                        ft.Column(
                            [
                                ft.Text(f"{slot.start.strftime('%Y-%m-%d %H:%M')} → {slot.end.strftime('%H:%M')}"),
                                ft.Text(f"Recursos: {res_names}", size=12),
                                ft.ElevatedButton("Usar", on_click=lambda e, s=slot: use_slot(s)),
                            ],
                            spacing=6,
                        ),
                        padding=12,
                    )
                )
            )

        self.page.update()

    def on_save(self, _):
        try:
            start_dt = parse_dt(self.date_tf.value, self.start_tf.value)
            end_dt = parse_dt(self.date_tf.value, self.end_tf.value)
        except Exception:
            snack(self.page, "Fecha u hora inválida.")
            return

        if not self.name_tf.value.strip():
            snack(self.page, "El nombre es obligatorio.")
            return

        if end_dt <= start_dt:
            snack(self.page, "Hora fin debe ser posterior a inicio.")
            return

        if not self.state.selected_resource_ids:
            snack(self.page, "Selecciona al menos un recurso.")
            return

        ev = Event(
            id=str(uuid4()),
            name=self.name_tf.value.strip(),
            description="",
            event_type=self.type_tf.value.strip(),
            start=start_dt,
            end=end_dt,
            resource_ids=list(self.state.selected_resource_ids),
        )

        violations = self.scheduler.validate_event(ev)
        if violations:
            show_dialog(self.page, "Conflictos detectados", "\n".join(f"• {v.message}" for v in violations))
            return

        self.db.upsert_event(ev.to_dict())
        snack(self.page, "Evento guardado.")
        self.on_any_change()