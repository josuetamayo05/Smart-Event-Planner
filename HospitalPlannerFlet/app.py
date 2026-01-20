import flet as ft
from datetime import datetime, date, timedelta
from uuid import uuid4
import json
from models.database_manager import DatabaseManager
from models.scheduler import Scheduler
from models.event import Event

def main(page: ft.Page):
    page.title = "Planificador hospitalario"
    try:
        page.window.width=1200
        page.window.height=720
    except Exception:
        pass
    
    db=DatabaseManager("database.json")
    scheduler=Scheduler(db)

    selected_index=0
    selected_resource_ids: set[str]=set()

    # calendar
    calendar_view = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
    calendar_date = date.today()
    resource_filter = ""  # "" = todos

    date_picker = ft.DatePicker(
        first_date=datetime(2020, 1, 1),
        last_date=datetime(2035, 12, 31),
        value=datetime.now(),  
    )

    def on_pick_date(e):
        nonlocal calendar_date
        if date_picker.value:
            calendar_date = date_picker.value.date()
            refresh_calendar_day()
            page.update()

    date_picker.on_change = on_pick_date
    page.overlay.append(date_picker)

    def open_calendar_date_picker(_):
        date_picker.open = True
        page.update()

    def refresh_calendar_day():
        calendar_view.controls.clear()
        calendar_view.controls.append(ft.Text("Calendario diario", size=22, weight=ft.FontWeight.BOLD))

        # filtro de recurso
        res_options = [ft.dropdown.Option("", "Todos")] + [
            ft.dropdown.Option(r["id"], r.get("name", r["id"])) for r in db.list_resources()
        ]
        filter_dd = ft.Dropdown(
            label="Filtrar por recurso",
            value=resource_filter,
            options=res_options,
        )

        def on_filter_change(e):
            nonlocal resource_filter
            resource_filter = e.control.value or ""
            refresh_calendar_day()
            page.update()

        filter_dd.on_change = on_filter_change

        calendar_view.controls.append(
            ft.Row(
                [
                    ft.Text(f"Fecha: {calendar_date.isoformat()}", size=14),
                    ft.ElevatedButton("Cambiar fecha", on_click=open_calendar_date_picker),
                    filter_dd,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )
        )

        # parámetros visuales del timeline
        DAY_START = 7
        DAY_END = 20
        PX_PER_MIN = 1.0  # 1 px por minuto => 13h = 780px de alto aprox
        timeline_height = int((DAY_END - DAY_START) * 60 * PX_PER_MIN)

        SLOT_MIN = 20
        slot_height = int(SLOT_MIN * PX_PER_MIN)

        def on_slot_click(minutes_of_day: int):
            # minutes_of_day ya viene absoluto (ej: 14:30 => 870)
            start_h, start_m = divmod(minutes_of_day, 60)
            end_minutes = min(DAY_END * 60, minutes_of_day + 60)  # default 60 min
            end_h, end_m = divmod(end_minutes, 60)

            date_tf.value = calendar_date.isoformat()
            start_tf.value = f"{start_h:02d}:{start_m:02d}"
            end_tf.value = f"{end_h:02d}:{end_m:02d}"

            # debug opcional
            snack(f"Nuevo evento {start_tf.value}-{end_tf.value}")

            go_to(2)  # Nuevo evento
        

        # cargar eventos del día
        day_events = []
        for e_dict in db.list_events():
            try:
                ev = Event.from_dict(e_dict)
            except Exception:
                continue
            if ev.start.date() != calendar_date:
                continue
            if resource_filter and resource_filter not in ev.resource_ids:
                continue
            day_events.append(ev)

        day_events.sort(key=lambda x: x.start)

        # fondo: horas
        slot_rows = []
        for m in range(DAY_START * 60, DAY_END * 60, SLOT_MIN):
            label = f"{m//60:02d}:00" if m % 60 == 0 else ""

            slot_rows.append(
                ft.Container(
                    height=slot_height,
                    ink=True,  # para que sea clickeable con efecto
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

        background = ft.Column(slot_rows, spacing=0)

        # eventos: tarjetas posicionadas
        event_cards = []
        for ev in day_events:
            start_min = (ev.start.hour * 60 + ev.start.minute) - (DAY_START * 60)
            end_min = (ev.end.hour * 60 + ev.end.minute) - (DAY_START * 60)

            # clamp por si hay eventos fuera del rango visual
            start_min = max(0, start_min)
            end_min = min((DAY_END - DAY_START) * 60, end_min)

            top = int(start_min * PX_PER_MIN)
            height = max(35, int((end_min - start_min) * PX_PER_MIN))

            # texto de recursos (opcional)
            res_names = []
            all_res = {r["id"]: r.get("name", r["id"]) for r in db.list_resources()}
            for rid in ev.resource_ids:
                res_names.append(all_res.get(rid, rid))
            res_text = ", ".join(res_names)

            card = ft.Container(
                left=80,
                right=10,
                top=top,
                height=height,
                bgcolor=ft.Colors.BLUE_100,
                border_radius=10,
                padding=10,
                on_click=lambda e, _ev=ev: open_event_dialog(_ev.to_dict()),
                content=ft.Column(
                    [
                        ft.Text(f"{ev.start.strftime('%H:%M')} - {ev.end.strftime('%H:%M')}  |  {ev.name}",
                                weight=ft.FontWeight.BOLD),
                        ft.Text(ev.event_type or "", size=12),
                        ft.Text(res_text, size=11, color=ft.Colors.GREY_700),
                    ],
                    spacing=4,
                ),
            )
            event_cards.append(card)

        

        timeline = ft.Container(
            height=timeline_height,
            content=ft.Stack([background, *event_cards]),
        )

        calendar_view.controls.append(
            ft.Container(
                border=ft.border.all(1, ft.Colors.GREY_300),
                border_radius=10,
                padding=10,
                content=ft.Column(
                    [timeline],
                    scroll=ft.ScrollMode.AUTO,
                    height=520,  # scroll vertical del día
                ),
            )
        )

    # UI helpers ----------------
    def snack(msg:str):
        page.snack_bar = ft.SnackBar(ft.Text(msg))
        page.snack_bar.open = True
        page.update()

    def open_dialog(dlg: ft.AlertDialog):
        if dlg not in page.overlay:
            page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def close_dialog(dlg: ft.AlertDialog):
        dlg.open = False
        page.update()
    
    def show_dialog(title: str, body: str):
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(body),
        )
        dlg.actions = [ft.TextButton("OK", on_click=lambda e: close_dialog(dlg))]
        open_dialog(dlg)

    def go_to(idx:int):
        nonlocal selected_index
        selected_index=idx
        render()

     # ---------------- Views ----------------
    dashboard_view = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
    events_view = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
    resources_view = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)

    # ---------------- Dashboard ----------------
    def refresh_dashboard():
        dashboard_view.controls.clear()
        events=db.list_events()
        resources=db.list_resources()
        
        dashboard_view.controls.append(ft.Text("Dashboard",size=22,weight=ft.FontWeight.BOLD))
        dashboard_view.controls.append(
            ft.Row(
                [
                    ft.Card(
                        ft.Container(
                            ft.Column([ft.Text("Eventos"), ft.Text(str(len(events)), size=20)]),
                            padding=12,
                        )
                    ),
                    ft.Card(
                        ft.Container(
                            ft.Column([ft.Text("Recursos"), ft.Text(str(len(resources)), size=20)]),
                            padding=12,
                        )
                    ),
                ]
            )
        )

        dashboard_view.controls.append(ft.Text("Próximos eventos:", size=16))
        if not events:
            dashboard_view.controls.append(ft.Text("No hay eventos guardados."))
        else:
            for e in sorted(events, key=lambda x: x.get("start", ""))[:10]:
                dashboard_view.controls.append(
                    ft.Text(f"- {e.get('start')} | {e.get('name')} ({e.get('event_type','')})")
                )


    def parse_dt(d_str:str, t_str: str)-> datetime:
        d = datetime.strptime(d_str.strip(), "%Y-%m-%d").date()
        t = datetime.strptime(t_str.strip(), "%H:%M").time()
        return datetime.combine(d, t)


    def open_event_dialog(existing:dict):
        name_edit=ft.TextField(label="Nombre", value=existing.get("name",""))
        type_edit=ft.TextField(label="Tipo",value=existing.get("event_type",""))

        start_iso = existing.get("start", "")
        end_iso = existing.get("end", "")

        date_edit = ft.TextField(label="Fecha (YYYY-MM-DD)", value=start_iso.split("T")[0] if "T" in start_iso else "")
        start_edit = ft.TextField(label="Hora inicio (HH:MM)", value=start_iso.split("T")[1] if "T" in start_iso else "09:00")
        end_edit = ft.TextField(label="Hora fin (HH:MM)", value=end_iso.split("T")[1] if "T" in end_iso else "11:00")

        # Recursos (checkboxes)
        selected_ids = set(existing.get("resource_ids", []))
        res_checks_col = ft.Column(spacing=2)

        def rebuild_checks():
            res_checks_col.controls.clear()
            for r in db.list_resources():
                rid = r["id"]
                rname = r.get("name", rid)

                def on_change(e, _rid=rid):
                    if e.control.value:
                        selected_ids.add(_rid)
                    else:
                        selected_ids.discard(_rid)

                res_checks_col.controls.append(
                    ft.Checkbox(label=rname, value=(rid in selected_ids), on_change=on_change)
                )
        
        rebuild_checks()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Editar evento"),
            content=ft.Column(
                [
                    name_edit,
                    type_edit,
                    ft.Row([date_edit, start_edit, end_edit]),
                    ft.Text("Recursos"),
                    ft.Container(res_checks_col, border=ft.border.all(1, ft.Colors.GREY_300), padding=10, height=180),
                ],
                tight=True,
                scroll=ft.ScrollMode.AUTO,
                height=520,
            ),
            actions=[],
        )

        def on_save(_):
            if not name_edit.value.strip():
                snack("El nombre es obligatorio.")
                return
            if not selected_ids:
                snack("Selecciona al menos un recurso.")
                return
            
            try:
                new_start = parse_dt(date_edit.value, start_edit.value)
                new_end = parse_dt(date_edit.value, end_edit.value)
            except Exception:
                snack("Fecha/hora inválidas.")
                return
            
            if new_end < new_start:
                snack("Hora fin debe ser mayor que inicio.")
                return 


            # Construir Event con el MISMO id (para que ignore el propio evento)
            ev = Event(
                id=existing["id"],
                name=name_edit.value.strip(),
                description=existing.get("description", ""),
                event_type=type_edit.value.strip(),
                start=new_start,
                end=new_end,
                resource_ids=list(selected_ids),
            )

            violations = scheduler.validate_event(ev)
            if violations:
                show_dialog("Conflictos detectados", "\n".join(f"• {v.message}" for v in violations))
                return

            db.upsert_event(ev.to_dict())
            close_dialog(dlg)
            snack("Evento actualizado.")
            refresh_dashboard()
            refresh_events_list()
            page.update()

        dlg.actions = [
            ft.TextButton("Cancelar", on_click=lambda e: close_dialog(dlg)),
            ft.ElevatedButton("Guardar cambios", on_click=on_save),
        ]

        open_dialog(dlg)


    # Events List
    def refresh_events_list():
        events_view.controls.clear()
        events_view.controls.append(ft.Text("Eventos", size=22, weight=ft.FontWeight.BOLD))
        events = sorted(db.list_events(), key=lambda x: x.get("start", ""))

        if not events:
            events_view.controls.append(ft.Text("No hay eventos."))
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

        def delete_event(event_id:str):
            db.delete_event(event_id)
            snack("Evento Eliminado.")
            refresh_dashboard()
            refresh_events_list()
            page.update()

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
                                    ft.IconButton(
                                        icon=ft.Icons.EDIT,
                                        tooltip="Editar",
                                        on_click=lambda ev, _e=e: open_event_dialog(_e),
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE,
                                        tooltip="Eliminar",
                                        on_click=lambda ev, _id=e["id"]: delete_event(_id),
                                    ),
                                ],
                                spacing=0,
                            )
                        )
                    ]
                )
            )

        events_view.controls.append(table)

    def refresh_resources_list():
        resources_view.controls.clear()
        resources_view.controls.append(ft.Text("Recursos", size=22, weight=ft.FontWeight.BOLD))

        resources = sorted(db.list_resources(), key=lambda r: r.get("name", ""))

        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Kind")),
                ft.DataColumn(ft.Text("Subtype")),
                ft.DataColumn(ft.Text("Role")),
                ft.DataColumn(ft.Text("Tags")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[],
        )

        def delete_resource(rid: str):
            db.delete_resource(rid)
            snack("Recurso eliminado.")
            refresh_resources_list()
            page.update()

        def open_resource_dialog(existing: dict | None = None):
            is_edit = existing is not None

            id_tf = ft.TextField(label="ID", value=(existing.get("id") if is_edit else ""))
            name_tf = ft.TextField(label="Nombre", value=(existing.get("name") if is_edit else ""))

            kind_dd = ft.Dropdown(
                label="Kind",
                options=[ft.dropdown.Option("physical"), ft.dropdown.Option("human")],
                value=(existing.get("kind") if is_edit else "physical"),
            )

            subtype_tf = ft.TextField(label="Subtype (si physical)", value=(existing.get("subtype") if is_edit else ""))
            role_tf = ft.TextField(label="Role (si human)", value=(existing.get("role") if is_edit else ""))
            tags_tf = ft.TextField(
                label="Tags (separados por coma)",
                value=",".join(existing.get("tags", [])) if is_edit else "",
            )

            def on_save_dialog(_):
                rid = (id_tf.value or "").strip()
                rname = (name_tf.value or "").strip()

                if not rid:
                    snack("ID es obligatorio.")
                    return
                if not rname:
                    snack("Nombre es obligatorio.")
                    return

                if is_edit and rid != existing["id"]:
                    snack("No se permite cambiar el ID al editar.")
                    return

                if not is_edit:
                    if any(r.get("id") == rid for r in db.list_resources()):
                        snack("Ya existe un recurso con ese ID.")
                        return

                kind = kind_dd.value
                subtype = (subtype_tf.value or "").strip() or None
                role = (role_tf.value or "").strip() or None
                tags = [t.strip() for t in (tags_tf.value or "").split(",") if t.strip()]

                db.upsert_resource(
                    {
                        "id": rid,
                        "name": rname,
                        "kind": kind,
                        "subtype": subtype,
                        "role": role,
                        "tags": tags,
                    }
                )

                close_dialog(dlg)
                snack("Recurso guardado.")
                refresh_resources_list()
                page.update()

            dlg = ft.AlertDialog(
                title=ft.Text("Editar recurso" if is_edit else "Nuevo recurso"),
                content=ft.Column(
                    [id_tf, name_tf, kind_dd, subtype_tf, role_tf, tags_tf],
                    tight=True,
                    scroll=ft.ScrollMode.AUTO,
                    height=360,
                ),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda e: close()),
                    ft.ElevatedButton("Guardar", on_click=on_save_dialog),
                ],
            )

            def close():
                close_dialog(dlg)

            open_dialog(dlg)

        resources_view.controls.append(
            ft.Row(
                [
                    ft.ElevatedButton("Nuevo recurso", on_click=lambda e: open_resource_dialog(None)),
                    ft.Text("Ej: quirófano => kind=physical, subtype='quirófano'.", italic=True),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )
        )

        for r in resources:
            table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(r.get("id", ""))),
                        ft.DataCell(ft.Text(r.get("name", ""))),
                        ft.DataCell(ft.Text(r.get("kind", ""))),
                        ft.DataCell(ft.Text(r.get("subtype") or "")),
                        ft.DataCell(ft.Text(r.get("role") or "")),
                        ft.DataCell(ft.Text(", ".join(r.get("tags", [])))),
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.IconButton(
                                        icon=getattr(ft.Icons, "EDIT", ft.Icons.EDIT_NOTE),
                                        tooltip="Editar",
                                        on_click=lambda e, _r=r: open_resource_dialog(_r),
                                    ),
                                    ft.IconButton(
                                        icon=getattr(ft.Icons, "DELETE", ft.Icons.DELETE_OUTLINE),
                                        tooltip="Eliminar",
                                        on_click=lambda e, _id=r["id"]: delete_resource(_id),
                                    ),
                                ],
                                spacing=0,
                            )
                        ),
                    ]
                )
            )

        resources_view.controls.append(table)

    # New event form
    name_tf = ft.TextField(label="Nombre del evento")
    type_tf = ft.TextField(label="Tipo (ej. cirugia_cardiaca)")
    date_tf = ft.TextField(label="Fecha (YYYY-MM-DD)", value=str(date.today()))
    start_tf = ft.TextField(label="Hora inicio (HH:MM)", value="09:00")
    end_tf = ft.TextField(label="Hora fin (HH:MM)", value="11:00")

    search_role_tf = ft.TextField(label="Rol requerido (ej: cardiologo)", value="")
    search_subtype_tf = ft.TextField(label="Subtype requerido (ej: quirófano)", value="quirófano")
    duration_tf = ft.TextField(label="Duración (minutos)", value="120")

    slots_column = ft.Column(spacing=6)

    validation_text = ft.Text("")  
    resources_column = ft.Column(spacing=2)

    
    def build_resources_checklist(preselected=None):
        preselected=set(preselected or [])
        resources_column.controls.clear()
        selected_resource_ids.clear()
        selected_resource_ids.update(preselected)

        for r in db.list_resources():
            rid=r["id"]
            rname=r.get("name",rid)

            def on_change(e,_rid=rid):
                if e.control.value:
                    selected_resource_ids.add(_rid)
                else:
                    selected_resource_ids.discard(_rid)
                quick_validate()

            resources_column.controls.append(
                ft.Checkbox(label=rname, value=(rid in preselected), on_change=on_change)
            )

    def on_find_slots(_):
        slots_column.controls.clear()

        fixed_ids = list(selected_resource_ids)
        if not fixed_ids:
            slots_column.controls.append(ft.Text("Selecciona primero el recurso fijo (ej: Quirófano 1) y vuelve a buscar."))
            page.update()
            return

        try:
            from_dt = parse_dt(date_tf.value, start_tf.value)
        except Exception:
            snack("Fecha/hora inválidas para iniciar la búsqueda.")
            page.update()
            return

        try:
            mins = int((duration_tf.value or "").strip())
            duration = timedelta(minutes=mins)
        except Exception:
            snack("Duración inválida (usa minutos, ej 120).")
            page.update()
            return

        event_type = (type_tf.value or "").strip()

        # AQUÍ: método autofill
        results = scheduler.find_next_slots_autofill(
            fixed_resource_ids=fixed_ids,
            event_type=event_type,
            duration=duration,
            from_dt=from_dt,
            max_results=3,
        )

        if not results:
            slots_column.controls.append(ft.Text("No se encontraron horarios disponibles con esos recursos."))
            page.update()
            return

        def use_slot(slot):
            date_tf.value = slot.start.strftime("%Y-%m-%d")
            start_tf.value = slot.start.strftime("%H:%M")
            end_tf.value = slot.end.strftime("%H:%M")

            # Marcar recursos sugeridos (incluye personal)
            pre = [r.id for r in slot.resources]
            build_resources_checklist(preselected=pre)

            quick_validate()
            page.update()
            snack("Horario y recursos aplicados al formulario.")

        for slot in results:
            res_names = ", ".join(r.name for r in slot.resources)
            slots_column.controls.append(
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

        page.update()


    def quick_validate():
        """Validación ligera en vivo (no guarda, solo muestra el primer conflicto)."""
        validation_text.value=""
        try:
            start_dt = parse_dt(date_tf.value, start_tf.value)
            end_dt = parse_dt(date_tf.value, end_tf.value)
        except Exception:
            validation_text.value = "Completa fecha/hora válidas (YYYY-MM-DD y HH:MM)."
            validation_text.color = ft.Colors.RED
            page.update()
            return
        
        if start_dt>=end_dt:
            validation_text.value = "La fecha de inicio debe ser menor que la final."
            validation_text.color=ft.Colors.RED
            page.update()
            return
        
        temp = Event(
            id="__tmp__",
            name=name_tf.value.strip() or "Evento",
            description="",
            event_type=type_tf.value.strip(),
            start=start_dt,
            end=end_dt,
            resource_ids=list(selected_resource_ids),
        )

        violations = scheduler.validate_event(temp)
        if violations:
            validation_text.value = violations[0].message
            validation_text.color = ft.Colors.RED
        else:
            validation_text.value = "Sin conflictos detectados."
            validation_text.color = ft.Colors.GREEN

        page.update()
    
    # validación en vivo al cambiar textos
    for tf in (name_tf, type_tf, date_tf, start_tf, end_tf):
        tf.on_change = lambda e: quick_validate()

    def on_save(_):
        try:
            start_dt = parse_dt(date_tf.value, start_tf.value)
            end_dt = parse_dt(date_tf.value, end_tf.value)
        except Exception:
            snack("Fecha u hora inválida. Usa YYYY-MM-DD y HH:MM.")
            return 
        
        if not name_tf.value.strip():
            snack("El nombre es obligatorio.")
            return 

        if end_dt <= start_dt:
            snack("La hora fin debe ser posterior a la hora inicio.")
            return
        if not selected_resource_ids:
            snack("Selecciona al menos un recurso.")
            return
        
        ev = Event(
            id=str(uuid4()),
            name=name_tf.value.strip(),
            description="",
            event_type=type_tf.value.strip(),
            start=start_dt,
            end=end_dt,
            resource_ids=list(selected_resource_ids),
        )

        violations=scheduler.validate_event(ev)
        if violations:
            show_dialog("Conflictos detectados", "\n".join(f"• {v.message}" for v in violations))
            return
        
        db.upsert_event(ev.to_dict())
        snack("Evento guardado.")
        # refrescar vistas
        refresh_dashboard()
        refresh_events_list()
        go_to(0)
    
    new_event_view = ft.Column(
        [
            ft.Text("Nuevo evento", size=22, weight=ft.FontWeight.BOLD),
            name_tf,
            type_tf,
            ft.Row([date_tf, start_tf, end_tf]),
            validation_text,

            ft.Divider(),
            ft.Text("Recursos (elige aquí el recurso fijo, ej: OR1)", size=16),
            ft.Container(resources_column, border=ft.border.all(1, ft.Colors.GREY_300), padding=10),

            ft.Divider(),
            ft.Text("Búsqueda inteligente (autofill)", size=16, weight=ft.FontWeight.BOLD),
            duration_tf,
            ft.ElevatedButton("Buscar próximo horario disponible", on_click=on_find_slots),
            slots_column,

            ft.ElevatedButton("Guardar", on_click=on_save),
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
    
    # ---------------- Layout ----------------
    content=ft.Container(expand=True,padding=15)
    nav=ft.NavigationRail(
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

    def render():
        nav.selected_index = selected_index

        if selected_index == 0:
            refresh_dashboard()
            content.content = dashboard_view

        elif selected_index == 1:
            refresh_events_list()
            content.content = events_view

        elif selected_index == 2:
            build_resources_checklist()
            quick_validate()
            content.content = new_event_view

        elif selected_index == 3:
            refresh_calendar_day()
            content.content = calendar_view

        elif selected_index == 4:
            refresh_resources_list()
            content.content = resources_view

        page.update()
    
    page.add(ft.Row([nav, ft.VerticalDivider(width=1), content], expand=True))
    render()

    


if __name__ == "__main__":
    ft.run(main)