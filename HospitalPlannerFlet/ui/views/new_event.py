from __future__ import annotations
import flet as ft
from datetime import date, timedelta
from uuid import uuid4

from ui.dialogs import snack, show_dialog, open_dialog, close_dialog
from ui.time_utils import parse_dt
from models.event import Event

from ui.design import prime_color, sec_color, light_color, dark_color, white_color, text_on_dark, text_on_light
from ui.catalogs.event_types import EVENT_TYPES

class NewEventView:
    def __init__(self, page: ft.Page, db, scheduler, state, on_any_change: callable):
        self.page = page
        self.db = db
        self.scheduler = scheduler
        self.state = state
        self.on_any_change = on_any_change

        flat_options=[]
        for cat,items in EVENT_TYPES.items():
            for it in items:
                flat_options.append(ft.dropdown.Option(it["code"],it["label"]))

        # Estilo base para inputs (solo diseño)
        base_tf_kwargs = dict(
            border_color=prime_color,
            color="black",
            bgcolor=ft.Colors.WHITE,
            filled=True,
            border_radius=14,
        )

        self.name_tf = ft.TextField(label="Nombre del evento", **base_tf_kwargs)
        self.type_tf = ft.Dropdown(label="Tipo de evento", options=flat_options, border_color=prime_color, color="black", bgcolor=ft.Colors.WHITE)
        self.date_tf = ft.TextField(label="Fecha (YYYY-MM-DD)", value=str(date.today()), **base_tf_kwargs)
        self.start_tf = ft.TextField(label="Hora inicio (HH:MM)", value="09:00", **base_tf_kwargs)
        self.end_tf = ft.TextField(label="Hora fin (HH:MM)", value="11:00", **base_tf_kwargs)

        self.duration_tf = ft.TextField(label="Duración (minutos)", value="120", **base_tf_kwargs)
        self.slots_column = ft.Column(spacing=6)
        self.validation_text = ft.Text("")
        self.resources_column = ft.Column(spacing=2)

        self.name_tf.on_change = lambda e: self.quick_validate()
        self.date_tf.on_change = lambda e: self.quick_validate()
        self.start_tf.on_change = lambda e: self.quick_validate()
        self.end_tf.on_change = lambda e: self.quick_validate()
        self.type_tf.on_change = lambda e: self.quick_validate()  
        self.duration_tf.on_change = lambda e: self.quick_validate()  

        self.type_tf.border_color=prime_color

        # panel desplegable
        def open_catalog(_):
            # función que se llama al hacer click en un item
            def pick_type(it: dict):
                self.type_tf.value = it["code"]
                if it.get("default_duration_min"):
                    self.duration_tf.value = str(it["default_duration_min"])
                self.quick_validate()
                close_dialog(self.page, dlg)
                self.page.update()

            tiles = []
            for cat, items in EVENT_TYPES.items():
                tiles.append(
                    ft.ExpansionTile(
                        title=ft.Text(cat, weight=ft.FontWeight.BOLD, color=text_on_light),
                        controls=[
                            ft.ListTile(
                                title=ft.Text(it["label"], color=text_on_light),
                                on_click=lambda e, it=it: pick_type(it),
                            )
                            for it in items
                        ],
                    )
                )

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
                            content=ft.Icon(ft.Icons.BOOKMARKS_OUTLINED, color=prime_color, size=20),
                        ),
                        ft.Text("Catálogo de tipos de evento", size=18, weight=ft.FontWeight.BOLD, color=text_on_light),
                    ],
                ),
                content=ft.Container(
                    width=520,
                    height=520,
                    padding=12,
                    border_radius=18,
                    bgcolor=ft.Colors.WHITE,
                    border=ft.border.all(1, ft.Colors.GREY_200),
                    shadow=[
                        ft.BoxShadow(
                            blur_radius=18,
                            spread_radius=1,
                            color=ft.Colors.BLACK12,
                            offset=ft.Offset(0, 8),
                        )
                    ],
                    content=ft.Column(tiles, scroll=ft.ScrollMode.AUTO),
                ),
                actions=[
                    ft.TextButton("Cerrar", on_click=lambda e: close_dialog(self.page, dlg)),
                ],
            )

            open_dialog(self.page, dlg)

        self.open_catalog_btn = ft.ElevatedButton(
            "Mostrar catálogo",
            icon=ft.Icons.MENU_BOOK_OUTLINED,
            bgcolor=sec_color,
            color="white",
            on_click=open_catalog,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=14),
                padding=ft.padding.symmetric(horizontal=16, vertical=12),
            ),
        )

        #helper
        def section(title: str, content: ft.Control):
            return ft.Container(
                padding=16,
                border_radius=18,
                bgcolor=ft.Colors.WHITE,
                border=ft.border.all(1, ft.Colors.GREY_200),
                shadow=[
                    ft.BoxShadow(
                        blur_radius=20,
                        spread_radius=1,
                        color=ft.Colors.BLACK12,
                        offset=ft.Offset(0, 10),
                    )
                ],
                content=ft.Column(
                    [
                        ft.Row(
                            spacing=10,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Container(
                                    width=34,
                                    height=34,
                                    border_radius=14,
                                    bgcolor=white_color,
                                    border=ft.border.all(1, ft.Colors.GREY_200),
                                    alignment=ft.Alignment(0, 0),
                                    content=ft.Icon(ft.Icons.CIRCLE, color=prime_color, size=10),
                                ),
                                ft.Text(title, size=14, weight=ft.FontWeight.W_700, color=prime_color),
                            ],
                        ),
                        content,
                    ],
                    spacing=12,
                ),
            )

        # Header superior (solo diseño)
        header = ft.Container(
            padding=18,
            border_radius=22,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=[prime_color, sec_color],
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
                                content=ft.Icon(ft.Icons.ADD_CIRCLE_OUTLINE, color=prime_color, size=24),
                            ),
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text("Nuevo evento", size=22, weight=ft.FontWeight.BOLD, color="white"),
                                    ft.Text("Completa los datos y valida conflictos", size=13, color=ft.Colors.WHITE),
                                ],
                            ),
                        ],
                    ),
                    ft.Container(
                        padding=10,
                        border_radius=16,
                        bgcolor=ft.Colors.with_opacity(0.18, ft.Colors.WHITE),
                        border=ft.border.all(1, ft.Colors.with_opacity(0.22, ft.Colors.WHITE)),
                        content=ft.Icon(ft.Icons.EVENT_AVAILABLE_OUTLINED, color="white", size=22),
                    ),
                ],
            ),
        )

        # Contenedor de validación (solo diseño)
        validation_box = ft.Container(
            padding=12,
            border_radius=16,
            bgcolor=ft.Colors.with_opacity(0.06, ft.Colors.BLACK),
            border=ft.border.all(1, ft.Colors.GREY_200),
            content=ft.Row(
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(ft.Icons.VERIFIED_OUTLINED, color=sec_color),
                    ft.Container(self.validation_text, expand=True),
                ],
            ),
        )

        # Lista de recursos (solo diseño)
        resources_box = ft.Container(
            padding=10,
            border_radius=16,
            bgcolor=white_color,
            border=ft.border.all(1, ft.Colors.GREY_200),
            content=ft.Column(
                [
                    ft.Container(
                        padding=ft.padding.only(bottom=6),
                        content=ft.Text(
                            "Marca los recursos necesarios. Si un recurso tiene pool, selecciona unidades.",
                            size=12,
                            color=ft.Colors.GREY_700,
                        ),
                    ),
                    ft.Container(self.resources_column, padding=6),
                ],
                spacing=8,
            ),
        )

        # Panel de búsqueda inteligente (solo diseño)
        smart_box = ft.Column(
            [
                self.duration_tf,
                ft.ElevatedButton(
                    "Buscar próximo horario disponible",
                    icon=ft.Icons.SEARCH,
                    bgcolor=sec_color,
                    color="white",
                    on_click=self.on_find_slots,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=14),
                        padding=ft.padding.symmetric(horizontal=18, vertical=12),
                    ),
                ),
                self.slots_column,
            ],
            spacing=10,
        )

        # Botón guardar (solo diseño)
        save_btn = ft.ElevatedButton(
            "Guardar",
            icon=ft.Icons.SAVE_OUTLINED,
            bgcolor=prime_color,
            color="white",
            on_click=self.on_save,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=14),
                padding=ft.padding.symmetric(horizontal=18, vertical=12),
            ),
        )

        form_panel = ft.Column(
            [
                header,
                section("Datos del evento",
                    ft.Column(
                        [
                            self.name_tf,
                            ft.Row(
                                [
                                    ft.Container(self.type_tf, expand=True),
                                    self.open_catalog_btn,
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=ft.CrossAxisAlignment.START,
                            ),
                            ft.Row([self.date_tf, self.start_tf, self.end_tf]),
                            validation_box,
                        ],
                        spacing=10,
                    ),
                ),

                section("Recursos (elige el fijo, ej: OR1)", resources_box,
                ),
                section("Búsqueda inteligente (autofill)",
                    smart_box,
                ),

                save_btn,
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=12,
        )

        self.view=form_panel


    def set_times(self, date_iso: str, start_hhmm: str, end_hhmm: str):
        self.date_tf.value = date_iso
        self.start_tf.value = start_hhmm
        self.end_tf.value = end_hhmm

    def build_resources_checklist(self, preselected=None,preselected_units=None):
        preselected = set(preselected or [])
        preselected_units=dict(preselected_units or {})

        self.resources_column.controls.clear()
        self.state.selected_resource_ids.clear()
        self.state.selected_resource_ids.update(preselected)

        self.state.resource_units.clear()
        # cargar unidades preseleccionadas si vienen
        for rid,u in preselected_units.items():
            self.state.resource_units[rid]=int(u)

        for r in self.db.list_resources():
            rid = r["id"]   
            rname = r.get("name", rid)
            qty=int(r.get("quantity",1)or 1)

            # selector de unidades para pool
            units_dd=None
            if qty>1:
                #valor por defecto si esta seleccionado
                default_units=self.state.resource_units.get(rid,1)
                default_units=max(1,min(qty,default_units))

                units_dd=ft.Dropdown(
                    width=120,
                    label="Unid.",
                    value=str(default_units),
                    options=[ft.dropdown.Option(str(i), str(i)) for i in range(1, qty + 1)],
                    disabled=(rid not in preselected),
                    border_color=prime_color,
                    bgcolor=ft.Colors.WHITE,
                    filled=True,
                )

                def on_units_change(e,_rid=rid):
                    self.state.resource_units[_rid]=int(e.control.value or 1)
                    self.quick_validate()
            
                units_dd.on_change=on_units_change
            
            #checkbox del producto
            cb=ft.Checkbox(label=rname, value=(rid in preselected))

            def on_check_change(e,_rid=rid,_qty=qty, _units_dd=units_dd):
                if e.control.value:
                    self.state.selected_resource_ids.add(_rid)
                    # si es pool, setea unidades por defecto y habilita dropdown
                    if _qty>1:
                        self.state.resource_units[_rid]=int((_units_dd.value or "1"))
                        _units_dd.disabled=False
                        _units_dd.update()
                else:
                    self.state.selected_resource_ids.discard(_rid)
                    # si es pool, limpiar unidades y resetear dropdown
                    if _qty>1:
                        self.state.resource_units.pop(_rid, None)
                        _units_dd.disabled=True
                        _units_dd.update()

                self.quick_validate()
            
            cb.on_change=on_check_change

            # layout por fila: checkbox + (unidades si aplica)
            row_controls = [ft.Container(cb, expand=True)]
            if units_dd is not None:
                row_controls.append(units_dd)

            # Fila con estilo suave (solo diseño)
            self.resources_column.controls.append(
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=10, vertical=8),
                    border_radius=14,
                    bgcolor=ft.Colors.with_opacity(0.30, white_color) if (rid in preselected) else ft.Colors.with_opacity(0.12, white_color),
                    border=ft.border.all(1, ft.Colors.GREY_200),
                    content=ft.Row(row_controls, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                )
            )
        self.page.update()
        self.quick_validate()

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
        
        etype=(self.type_tf.value or "").strip()
        if not etype:
            self.validation_text.value="Selecciona un tipo de evento."
            self.validation_text.color=ft.Colors.RED
            self.page.update()
            return

        temp = Event(
            id="__tmp__",
            name=self.name_tf.value.strip() or "Evento",
            description="",
            event_type=etype,
            start=start_dt,
            end=end_dt,
            resource_ids=list(self.state.selected_resource_ids),
            resource_units=dict(self.state.resource_units),
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
            units={}
            for r in slot.resources:
                if getattr(r,"quantity",1)>1:
                    units[r.id]=1
            self.build_resources_checklist(preselected=pre,preselected_units=units)
            self.quick_validate()
            self.page.update()
            snack(self.page, "Horario y recursos aplicados al formulario.")

        for slot in results:
            res_names = ", ".join(r.name for r in slot.resources)

            # Tarjeta de slot (solo diseño)
            self.slots_column.controls.append(
                ft.Container(
                    padding=14,
                    border_radius=18,
                    bgcolor=ft.Colors.WHITE,
                    border=ft.border.all(1, ft.Colors.GREY_200),
                    shadow=[
                        ft.BoxShadow(
                            blur_radius=18,
                            spread_radius=1,
                            color=ft.Colors.BLACK12,
                            offset=ft.Offset(0, 8),
                        )
                    ],
                    content=ft.Column(
                        [
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Row(
                                        spacing=10,
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        controls=[
                                            ft.Container(
                                                width=34,
                                                height=34,
                                                border_radius=14,
                                                bgcolor=ft.Colors.with_opacity(0.14, sec_color),
                                                alignment=ft.Alignment(0, 0),
                                                content=ft.Icon(ft.Icons.SCHEDULE, color=sec_color, size=18),
                                            ),
                                            ft.Text(
                                                f"{slot.start.strftime('%Y-%m-%d %H:%M')} → {slot.end.strftime('%H:%M')}",
                                                weight=ft.FontWeight.BOLD,
                                                color=text_on_light,
                                            ),
                                        ],
                                    ),
                                    ft.ElevatedButton(
                                        "Usar",
                                        icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
                                        on_click=lambda e, s=slot: use_slot(s),
                                        bgcolor=prime_color,
                                        color="white",
                                        style=ft.ButtonStyle(
                                            shape=ft.RoundedRectangleBorder(radius=14),
                                            padding=ft.padding.symmetric(horizontal=14, vertical=10),
                                        ),
                                    ),
                                ],
                            ),
                            ft.Text(f"Recursos: {res_names}", size=12, color=ft.Colors.GREY_700),
                        ],
                        spacing=8,
                    ),
                )
            )

        self.page.update()

    def reset_form(self):
        self.name_tf.value = ""
        self.type_tf.value = None
        self.date_tf.value = str(date.today())
        self.start_tf.value = "09:00"
        self.end_tf.value = "11:00"
        self.duration_tf.value = "120"

        self.slots_column.controls.clear()
        self.validation_text.value = ""
        self.validation_text.color = None

        self.state.selected_resource_ids.clear()
        self.state.resource_units.clear()

        self.build_resources_checklist(preselected=[], preselected_units={})
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
        
        etype=(self.type_tf.value or "").strip()
        if not etype:
            snack(self.page, "Selecciona un tipo de evento.")
            return

        ev = Event(
            id=str(uuid4()),
            name=self.name_tf.value.strip(),
            description="",
            event_type=etype,
            start=start_dt,
            end=end_dt,
            resource_ids=list(self.state.selected_resource_ids),
            resource_units=dict(self.state.resource_units)
        )

        violations = self.scheduler.validate_event(ev)
        if violations:
            show_dialog(self.page, "Conflictos detectados", "\n".join(f"• {v.message}" for v in violations))
            return

        self.db.upsert_event(ev.to_dict())
        show_dialog(self.page, "Éxito", "Evento guardado correctamente.")  # más visible que snack
        self.on_any_change()
        self.reset_form()