from __future__ import annotations
import flet as ft
from ui.design import *

class SearchView:
    def __init__(self,page:ft.Page,db, go_to):
        self.page=page
        self.db=db
        self.view=ft.Column(spacing=12, scroll=ft.ScrollMode.AUTO)

        self.go_to=go_to

        # Estilo consistente con el resto de pestañas (solo diseño)
        self.query_tf = ft.TextField(
            label="Buscar",
            hint_text="Ej: quirofano, trasplante, DR_AN1, tomografo, 2026-01-20",
            border_color=prime_color,
            color="black",
            bgcolor=ft.Colors.WHITE,
            filled=True,
            border_radius=14,
            prefix_icon=ft.Icons.SEARCH,
        )

        self.scope_rg = ft.RadioGroup(
            value="all",
            content=ft.Row(
                [
                    ft.Radio(value="all", label="Todo"),
                    ft.Radio(value="events", label="Eventos"),
                    ft.Radio(value="resources", label="Recursos"),
                ],
                spacing=20,
            ),
        )
        self.scope_rg.on_change = lambda e: self._do_search(scope_override=self.scope_rg.value)

        self.query_tf.on_change = lambda e: self._do_search()
        self.query_tf.on_submit = lambda e: self._do_search()

        self.results=ft.ListView(expand=True,spacing=8,padding=0)

        # --- Helpers de diseño (solo UI) ---
        def card(content, padding=16, radius=18, bgcolor=ft.Colors.WHITE):
            return ft.Container(
                padding=padding,
                border_radius=radius,
                bgcolor=bgcolor,
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

        #construir layout
        self.view.controls=[
            # Header moderno (igual estilo que otras pestañas)
            ft.Container(
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
                                    content=ft.Icon(ft.Icons.MANAGE_SEARCH_OUTLINED, color=prime_color, size=24),
                                ),
                                ft.Column(
                                    spacing=2,
                                    controls=[
                                        ft.Text("Buscar", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                        ft.Text(
                                            "Encuentra eventos y recursos rápidamente",
                                            size=13,
                                            color=ft.Colors.with_opacity(0.92, ft.Colors.WHITE),
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        ft.Container(
                            padding=10,
                            border_radius=16,
                            bgcolor=ft.Colors.with_opacity(0.18, ft.Colors.WHITE),
                            border=ft.border.all(1, ft.Colors.with_opacity(0.22, ft.Colors.WHITE)),
                            content=ft.Icon(ft.Icons.SEARCH, color=ft.Colors.WHITE, size=22),
                        ),
                    ],
                ),
            ),

            # Panel de búsqueda (card pro)
            card(
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Container(self.query_tf, expand=True),
                                ft.Container(width=12),
                                ft.Container(
                                    padding=ft.padding.symmetric(horizontal=12, vertical=8),
                                    border_radius=16,
                                    bgcolor=ft.Colors.with_opacity(0.55, white_color),
                                    border=ft.border.all(1, ft.Colors.GREY_200),
                                    content=self.scope_rg,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            vertical_alignment=ft.CrossAxisAlignment.START,
                        ),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Text("Resultados:", size=14, weight=ft.FontWeight.W_700, color=text_on_light),
                                ft.Container(
                                    padding=ft.padding.symmetric(horizontal=10, vertical=6),
                                    border_radius=999,
                                    bgcolor=ft.Colors.with_opacity(0.12, dark_color),
                                    border=ft.border.all(1, ft.Colors.with_opacity(0.18, dark_color)),
                                    content=ft.Row(
                                        spacing=8,
                                        tight=True,
                                        controls=[
                                            ft.Icon(ft.Icons.FILTER_ALT_OUTLINED, size=18, color=dark_color),
                                            ft.Text("Filtro", size=12, weight=ft.FontWeight.BOLD, color=text_on_light),
                                        ],
                                    ),
                                ),
                            ],
                        ),
                        ft.Container(
                            height=520,
                            border_radius=16,
                            bgcolor=ft.Colors.with_opacity(0.35, white_color),
                            border=ft.border.all(1, ft.Colors.GREY_200),
                            padding=12,
                            content=self.results,
                        ),
                    ],
                    spacing=12,
                ),
                padding=16,
                radius=18,
            ),
        ]

    def refresh(self):
        self._do_search() #refrescar por si cambio db

    # helpers
    def _match_text(self,text:str,tokens:list[str])->bool:
        t=(text or "").lower()
        return all(tok in t for tok in tokens)
    
    def _event_card(self,e:dict)->ft.Control:
        title = f"{e.get('start','')} | {e.get('name','')}"
        subtitle = f"Tipo: {e.get('event_type','')} | Recursos: {len(e.get('resource_ids', []))}"

        def go_events(_):
            self.go_to(1)

        def show_details(_):
            dlg = ft.AlertDialog(
                modal=True,
                bgcolor=ft.Colors.with_opacity(0.92, white_color),
                title=ft.Row(
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            width=38,
                            height=38,
                            border_radius=14,
                            bgcolor=ft.Colors.with_opacity(0.14, prime_color),
                            border=ft.border.all(1, ft.Colors.with_opacity(0.20, prime_color)),
                            alignment=ft.Alignment(0, 0),
                            content=ft.Icon(ft.Icons.EVENT_NOTE_OUTLINED, color=prime_color, size=20),
                        ),
                        ft.Text("Detalle del evento", size=18, weight=ft.FontWeight.W_700, color=text_on_light),
                    ],
                ),
                content=ft.Container(
                    width=420,
                    padding=18,
                    border_radius=22,
                    bgcolor=ft.Colors.with_opacity(0.10, light_color),
                    border=ft.border.all(1, ft.Colors.with_opacity(0.20, light_color)),
                    shadow=[
                        ft.BoxShadow(
                            blur_radius=24,
                            spread_radius=1,
                            color=ft.Colors.with_opacity(0.12, "#0B1220"),
                            offset=ft.Offset(0, 12),
                        )
                    ],
                    blur=ft.Blur(12, 12, ft.BlurTileMode.MIRROR),
                    content=ft.Text(
                        f"ID: {e.get('id','')}\n"
                        f"Nombre: {e.get('name','')}\n"
                        f"Tipo: {e.get('event_type','')}\n"
                        f"Inicio: {e.get('start','')}\n"
                        f"Fin: {e.get('end','')}\n"
                        f"Recursos: {', '.join(e.get('resource_ids', []))}",
                        size=13,
                        color=text_on_light,
                        selectable=True,
                    ),
                ),
                actions_alignment=ft.MainAxisAlignment.END,
                actions=[ft.TextButton("Cerrar", on_click=lambda x: self._close_dialog(dlg))],
            )
            self._open_dialog(dlg)

        # Tarjeta estilo “pro” (solo diseño)
        return ft.Container(
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
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                width=34,
                                height=34,
                                border_radius=14,
                                bgcolor=ft.Colors.with_opacity(0.14, prime_color),
                                border=ft.border.all(1, ft.Colors.with_opacity(0.18, prime_color)),
                                alignment=ft.Alignment(0, 0),
                                content=ft.Icon(ft.Icons.EVENT_AVAILABLE_OUTLINED, color=prime_color, size=18),
                            ),
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(title, size=12, weight=ft.FontWeight.W_700, color=text_on_light),
                                    ft.Text(subtitle, size=11, color=ft.Colors.GREY_700),
                                ],
                            ),
                        ],
                    ),
                    ft.Row(
                        [
                            ft.TextButton(
                                "Ver",
                                on_click=show_details,
                                style=ft.ButtonStyle(color=prime_color),
                            ),
                            ft.TextButton(
                                "Ir a Eventos",
                                on_click=go_events,
                                style=ft.ButtonStyle(color=sec_color),
                            ),
                        ],
                        spacing=10,
                    ),
                ],
                spacing=10,
            ),
        )
    
    def _resource_card(self, r: dict) -> ft.Control:
        rid = r.get("id", "")
        name = r.get("name", "")
        kind = r.get("kind", "")
        subtype = r.get("subtype") or ""
        role = r.get("role") or ""
        qty = r.get("quantity", 1)
        tags = ", ".join(r.get("tags", []))

        line1 = f"{rid} | {name}"
        line2 = f"kind={kind} subtype={subtype} role={role} qty={qty}"
        line3 = f"tags: {tags}" if tags else "tags: -"

        def go_resources(_):
            self.go_to(4) 

        def show_details(_):
            dlg = ft.AlertDialog(
                modal=True,
                bgcolor=ft.Colors.with_opacity(0.92, white_color),
                title=ft.Row(
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            width=38,
                            height=38,
                            border_radius=14,
                            bgcolor=ft.Colors.with_opacity(0.14, prime_color),
                            border=ft.border.all(1, ft.Colors.with_opacity(0.20, prime_color)),
                            alignment=ft.Alignment(0,0),
                            content=ft.Icon(ft.Icons.EVENT_NOTE_OUTLINED, color=prime_color, size=20),
                        ),
                        ft.Text(
                            "Detalle del evento",
                            size=18,
                            weight=ft.FontWeight.W_700,
                            color=text_on_light,
                        ),
                    ],
                ),
                content=ft.Container(
                    width=420,  # ajusta si lo quieres más ancho/estrecho
                    padding=18,
                    border_radius=22,
                    bgcolor=ft.Colors.with_opacity(0.10, light_color),
                    border=ft.border.all(1, ft.Colors.with_opacity(0.20, light_color)),
                    shadow=[
                        ft.BoxShadow(
                            blur_radius=24,
                            spread_radius=1,
                            color=ft.Colors.with_opacity(0.12, "#0B1220"),
                            offset=ft.Offset(0, 12),
                        )
                    ],
                    blur=ft.Blur(12, 12, ft.BlurTileMode.MIRROR),
                    content=ft.Text(
                        f"ID: {r.get('id','')}\n"
                        f"Nombre: {r.get('name','')}\n"
                        f"Tipo: {r.get('event_type','')}\n"
                        f"Inicio: {r.get('start','')}\n"
                        f"Fin: {r.get('end','')}\n"
                        f"Recursos: {', '.join(r.get('resource_ids', []))}",
                        size=13,
                        color=text_on_light,
                        selectable=True,
                    ),
                ),
                actions_alignment=ft.MainAxisAlignment.END,
                actions=[
                    ft.TextButton(
                        "Cerrar",
                        on_click=lambda x: self._close_dialog(dlg),
                        style=ft.ButtonStyle(
                            color=prime_color,
                            overlay_color=ft.Colors.with_opacity(0.08, prime_color),
                        ),
                    )
                ],
            )
            self._open_dialog(dlg)

        # Tarjeta estilo “pro” (solo diseño)
        return ft.Container(
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
                                content=ft.Icon(ft.Icons.INVENTORY_2_OUTLINED, color=dark_color, size=18),
                            ),
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(line1, size=12, weight=ft.FontWeight.W_700, color=text_on_light),
                                    ft.Text(line2, size=11, color=ft.Colors.GREY_700),
                                    ft.Text(line3, size=11, color=ft.Colors.GREY_700),
                                ],
                            ),
                        ],
                    ),
                    ft.Row(
                        [
                            ft.TextButton(
                                "Ver",
                                on_click=show_details,
                                style=ft.ButtonStyle(color=prime_color),
                            ),
                            ft.TextButton(
                                "Ir a Recursos",
                                on_click=go_resources,
                                style=ft.ButtonStyle(color=sec_color),
                            ),
                        ],
                        spacing=10,
                    ),
                ],
                spacing=10,
            ),
        )
    
    def _open_dialog(self, dlg: ft.AlertDialog):
        if dlg not in self.page.overlay:
            self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()

    def _close_dialog(self, dlg: ft.AlertDialog):
        dlg.open = False
        self.page.update()
    
    def _do_search(self, scope_override=None):
        q = (self.query_tf.value or "").strip().lower()
        scope = (scope_override or "all").strip().lower()
        tokens=[t for t in q.split() if t]

        self.results.controls.clear()

        if not tokens:
            self.results.controls.append(
                ft.Text("Escribe algo para buscar. Ejemplos: 'quirofano', 'trasplante', 'DR_AN1', 'tomografo'",
                        color=ft.Colors.GREY_700)
            )
            self.page.update()
            return

        if scope in ("all", "events"):
            events=self.db.list_events()
            found_events=[]
            for e in events:
                haystack=" ".join([
                    e.get("id", ""),
                    e.get("name", ""),
                    e.get("event_type", ""),
                    e.get("start", ""),
                    e.get("end", ""),
                    " ".join(e.get("resource_ids", [])),
                ])
                if self._match_text(haystack,tokens):
                    found_events.append(e)

            found_events=sorted(found_events, key=lambda x:x.get("start",""))[:50]
            if found_events:
                self.results.controls.append(ft.Text("Eventos",size=12,weight=ft.FontWeight.BOLD,color=dark_color))
                for e in found_events:
                    self.results.controls.append(self._event_card(e))

        #buscar recursos
        if scope in ("all","resources"):
            resources=self.db.list_resources()
            found_resources=[]
            for r in resources:
                haystack=" ".join([
                    r.get("id", ""),
                    r.get("name", ""),
                    r.get("kind", ""),
                    str(r.get("subtype", "") or ""),
                    str(r.get("role", "") or ""),
                    " ".join(r.get("tags", [])),
                ])
                if self._match_text(haystack, tokens):
                    found_resources.append(r)
            
            found_resources=sorted(found_resources, key=lambda x: x.get("name", ""))[:50]
            if found_resources:
                self.results.controls.append(ft.Text("Recursos",size=12,weight=ft.FontWeight.BOLD,color=dark_color))
                for r in found_resources:
                    self.results.controls.append(self._resource_card(r))
        
        if not self.results.controls:
            self.results.controls.append(ft.Text("Sin resultados.",color=ft.Colors.GREY_700))
        
        self.page.update()