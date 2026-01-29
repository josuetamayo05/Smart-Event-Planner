from __future__ import annotations
import flet as ft
from ui.dialogs import snack, open_dialog, close_dialog
from ui.catalogs.resource_types import RESOURCE_CATALOG
from ui.design import *

class ResourcesView:
    def __init__(self, page: ft.Page, db):
        self.page = page
        self.db = db
        self.view = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)

    def refresh(self):
        self.view.controls.clear()

        # --- Helpers visuales (solo UI) ---
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
                bgcolor=white_color,  # suave
                border=ft.border.all(1, ft.Colors.GREY_200),
                content=ft.Row(
                    spacing=8,
                    tight=True,
                    controls=[
                        ft.Icon(icon, size=18, color=sec_color),
                        ft.Text(text, size=13, weight=ft.FontWeight.W_600, color=text_on_light),
                    ],
                ),
            )

        resources = sorted(self.db.list_resources(), key=lambda r: r.get("name", ""))

        table = ft.DataTable(
            column_spacing=18,
            horizontal_margin=12,
            divider_thickness=0.6,
            heading_row_height=46,
            data_row_min_height=46,
            data_row_max_height=56,
            columns=[
                ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD, color=text_on_light)),
                ft.DataColumn(ft.Text("Nombre", weight=ft.FontWeight.BOLD, color=text_on_light)),
                ft.DataColumn(ft.Text("Kind", weight=ft.FontWeight.BOLD, color=text_on_light)),
                ft.DataColumn(ft.Text("Subtype", weight=ft.FontWeight.BOLD, color=text_on_light)),
                ft.DataColumn(ft.Text("Role", weight=ft.FontWeight.BOLD, color=text_on_light)),
                ft.DataColumn(ft.Text("Tags", weight=ft.FontWeight.BOLD, color=text_on_light)),
                ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD, color=text_on_light)),
            ],
            rows=[],
        )

        def delete_resource(rid: str):
            self.db.delete_resource(rid)
            snack(self.page, "Recurso eliminado.")
            self.refresh()
            self.page.update()

        def open_resource_dialog(existing: dict | None = None):
            is_edit = existing is not None
            existing = existing or {}

            subtype_options = [
                ft.dropdown.Option(it["code"], it["label"])
                for it in RESOURCE_CATALOG["Físicos (subtype)"]
            ]
            role_options = [
                ft.dropdown.Option(it["code"], it["label"])
                for it in RESOURCE_CATALOG["Humanos (role)"]
            ]

            id_tf = ft.TextField(label="ID", value=(existing.get("id", "") if is_edit else ""))
            name_tf = ft.TextField(label="Nombre", value=(existing.get("name", "") if is_edit else ""))

            kind_rg = ft.RadioGroup(
                value=(existing.get("kind") if is_edit else "physical"),
                content=ft.Row(
                    [
                        ft.Radio(value="physical", label="physical"),
                        ft.Radio(value="human", label="human"),
                    ],
                    spacing=20,
                ),
            )

            subtype_dd = ft.Dropdown(
                label="Subtype (físico)",
                options=subtype_options,
                value=(existing.get("subtype") if is_edit else None),
            )

            role_dd = ft.Dropdown(
                label="Role (humano)",
                options=role_options,
                value=(existing.get("role") if is_edit else None),
            )

            selected_tags = set(existing.get("tags", [])) if is_edit else set()
            tags_preview = ft.Text("")

            quantity_tf=ft.TextField(
                label="Cantidad",
                value=str(existing.get("quantity",1) if is_edit else 1),
                keyboard_type=ft.KeyboardType.NUMBER,
                width=160,
            )

            def get_qty()->int:
                try:
                    return int((quantity_tf.value or "1").strip())
                except Exception:
                    return 1
            
            def set_qty(v:int):
                v=max(1,int(v))
                quantity_tf.value=str(v)
                quantity_tf.update()
            
            qty_row=ft.Row(
                spacing=10,
                controls=[
                    ft.IconButton(ft.Icons.REMOVE, on_click=lambda e: set_qty(get_qty()-1)),
                    quantity_tf,
                    ft.IconButton(ft.Icons.ADD,on_click=lambda e: set_qty(get_qty()+1)),
                ],
            )
            

            def refresh_tags_preview():
                if not selected_tags:
                    tags_preview.value = "Sin tags"
                    tags_preview.color = ft.Colors.GREY_600
                else:
                    tags_preview.value = ", ".join(sorted(selected_tags))
                    tags_preview.color = None

            refresh_tags_preview()

            def open_tags_editor(_):
                temp_tags = set(selected_tags)
                tag_options = RESOURCE_CATALOG.get("Tags sugeridos", [])
                checks_col = ft.Column(spacing=2)

                def rebuild_checks():
                    checks_col.controls.clear()
                    for t in tag_options:
                        code = t["code"]
                        label = t["label"]

                        def on_change(e, _code=code):
                            if e.control.value:
                                temp_tags.add(_code)
                            else:
                                temp_tags.discard(_code)

                        checks_col.controls.append(
                            ft.Checkbox(label=label, value=(code in temp_tags), on_change=on_change)
                        )

                rebuild_checks()

                custom_tf = ft.TextField(
                    label="Tags extra (coma) (opcional)",
                    hint_text="Ej: esteril, pediatrico",
                    value="",
                )

                tags_dlg = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Editar tags"),
                    content=ft.Column(
                        [
                            ft.Text("Tags sugeridos"),
                            ft.Container(
                                checks_col,
                                border=ft.border.all(1, ft.Colors.GREEN_300),
                                padding=10,
                                height=220,
                            ),
                            custom_tf,
                        ],
                        tight=True,
                        scroll=ft.ScrollMode.AUTO,
                        height=520,
                    ),
                    actions=[],
                )
                

                def on_save_tags(e):
                    extra = [t.strip() for t in (custom_tf.value or "").split(",") if t.strip()]
                    temp_tags.update(extra)

                    selected_tags.clear()
                    selected_tags.update(temp_tags)

                    close_dialog(self.page, tags_dlg)
                    refresh_tags_preview()
                    self.page.update()

                tags_dlg.actions = [
                    ft.TextButton("Cancelar", on_click=lambda e: close_dialog(self.page, tags_dlg)),
                    ft.ElevatedButton("Guardar", on_click=on_save_tags),
                ]
                open_dialog(self.page, tags_dlg)

                def on_save_pool(e):
                    pass
                    

            edit_tags_btn = ft.ElevatedButton("Editar tags", on_click=open_tags_editor)

            def open_catalog_for_subtype(_):
                items = RESOURCE_CATALOG["Físicos (subtype)"]

                def pick(it: dict):
                    subtype_dd.value = it["code"]
                    close_dialog(self.page, cat_dlg)
                    self.page.update()

                cat_dlg = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Catálogo (Subtype físico)"),
                    content=ft.Container(
                        width=520,
                        height=520,
                        content=ft.Column(
                            [
                                ft.ListTile(
                                    title=ft.Text(it["label"]),
                                    on_click=lambda e, it=it: pick(it)
                                )
                                for it in items
                            ],
                            scroll=ft.ScrollMode.AUTO,
                        ),
                    ),
                    actions=[ft.TextButton("Cerrar", on_click=lambda e: close_dialog(self.page, cat_dlg))],
                )
                open_dialog(self.page, cat_dlg)

            def open_catalog_for_role(_):
                items = RESOURCE_CATALOG["Humanos (role)"]

                def pick(it: dict):
                    role_dd.value = it["code"]
                    close_dialog(self.page, cat_dlg)
                    self.page.update()

                cat_dlg = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Catálogo (Role humano)"),
                    content=ft.Container(
                        width=520,
                        height=520,
                        content=ft.Column(
                            [
                                ft.ListTile(
                                    title=ft.Text(it["label"]),
                                    on_click=lambda e, it=it: pick(it)
                                )
                                for it in items
                            ],
                            scroll=ft.ScrollMode.AUTO,
                        ),
                    ),
                    actions=[ft.TextButton("Cerrar", on_click=lambda e: close_dialog(self.page, cat_dlg))],
                )
                open_dialog(self.page, cat_dlg)

            catalog_btn_subtype = ft.ElevatedButton("Catálogo subtype", on_click=open_catalog_for_subtype)
            catalog_btn_role = ft.ElevatedButton("Catálogo role", on_click=open_catalog_for_role)

            subtype_row = ft.Row([ft.Container(subtype_dd, expand=True), catalog_btn_subtype])
            role_row = ft.Row([ft.Container(role_dd, expand=True), catalog_btn_role])

            def apply_kind_state(update_ui: bool = False):
                is_human = (kind_rg.value == "human")

                subtype_dd.disabled = is_human
                role_dd.disabled = not is_human

                subtype_row.visible = not is_human
                role_row.visible = is_human

                if is_human:
                    subtype_dd.value = None
                    quantity_tf.value="1"
                    quantity_tf.disabled=True
                else:
                    role_dd.value = None
                    quantity_tf.disabled=False

                if update_ui:
                    subtype_dd.update()
                    role_dd.update()
                    subtype_row.update()
                    role_row.update()
                    quantity_tf.update()

            def on_kind_change(e):
                snack(self.page, f"Kind cambiado a: {kind_rg.value}")
                apply_kind_state(update_ui=True)

            kind_rg.on_change = on_kind_change
            apply_kind_state(update_ui=False)

            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("Editar recurso" if is_edit else "Nuevo recurso"),
                content=ft.Column(
                    [
                        id_tf,
                        name_tf,
                        ft.Text("Kind"),
                        kind_rg,
                        ft.Text("Cantidad"),
                        qty_row,
                        subtype_row,
                        role_row,
                        ft.Row(
                            [
                                ft.Text("Tags", weight=ft.FontWeight.BOLD),
                                edit_tags_btn,
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        tags_preview
                    ],
                    tight=True,
                    scroll=ft.ScrollMode.AUTO,
                    height=520,
                ),
                actions=[],
            )

            def on_save(_):
                rid = (id_tf.value or "").strip()
                rname = (name_tf.value or "").strip()
                try:
                    quantity=int((quantity_tf.value or "1").strip())
                except Exception:
                    snack(self.page, "Cantidad inválida. Usa un número entero.")
                if quantity<1:
                    snack(self.page, "Cantidad debe ser mayor que 0")
                if not rid:
                    snack(self.page, "ID es obligatorio.")
                    return
                if not rname:
                    snack(self.page, "Nombre es obligatorio.")
                    return

                if is_edit and rid != existing.get("id"):
                    snack(self.page, "No se permite cambiar el ID al editar.")
                    return

                if (not is_edit) and any(r.get("id") == rid for r in self.db.list_resources()):
                    snack(self.page, "Ya existe un recurso con ese ID.")
                    return

                if kind_rg.value == "physical" and not subtype_dd.value:
                    snack(self.page, "Selecciona un subtype para recursos físicos.")
                    return
                if kind_rg.value == "human" and not role_dd.value:
                    snack(self.page, "Selecciona un role para recursos humanos.")
                    quantity=1
                    return

                tags = sorted(set(selected_tags))

                self.db.upsert_resource({
                    "id": rid,
                    "name": rname,
                    "kind": kind_rg.value,
                    "subtype": subtype_dd.value if kind_rg.value == "physical" else None,
                    "role": role_dd.value if kind_rg.value == "human" else None,
                    "tags": tags,
                    "quantity": quantity
                })

                close_dialog(self.page, dlg)
                snack(self.page, "Recurso guardado.")
                self.refresh()
                self.page.update()

            dlg.actions = [
                ft.TextButton("Cancelar", on_click=lambda e: close_dialog(self.page, dlg)),
                ft.ElevatedButton("Guardar", on_click=on_save),
            ]

            open_dialog(self.page, dlg)
            # ----------- FIN TU CÓDIGO ORIGINAL -----------

        # ---------------------------
        # Header moderno (gradiente)
        # ---------------------------
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
                                content=ft.Icon(ft.Icons.INVENTORY_2_OUTLINED, color=prime_color, size=22),
                            ),
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text("Recursos", size=22, weight=ft.FontWeight.W_800, color="white"),
                                    ft.Text("Gestiona recursos físicos y humanos", size=13, color=ft.Colors.WHITE),
                                ],
                            ),
                        ],
                    ),
                    ft.Container(
                        padding=10,
                        border_radius=16,
                        bgcolor=ft.Colors.WHITE,
                        content=ft.Text(str(len(resources)), weight=ft.FontWeight.W_800, color=prime_color),
                    ),
                ],
            ),
        )
        self.view.controls.append(header)

        # ---------------------------
        # Barra de acciones (card)
        # ---------------------------
        actions_bar = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.ElevatedButton(
                    "Nuevo recurso",
                    icon=ft.Icons.ADD,
                    bgcolor=prime_color,
                    color="white",
                    on_click=lambda e: open_resource_dialog(None),
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=14),
                        padding=ft.padding.symmetric(horizontal=18, vertical=12),
                    ),
                ),
                pill("Ej: quirófano → kind=physical, subtype='quirofano'", ft.Icons.INFO_OUTLINE),
            ],
        )
        self.view.controls.append(card(actions_bar, padding=14, radius=18))

        # ---------------------------
        # Llenar tabla (sin tocar lógica)
        # ---------------------------
        for r in resources:
            table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(r.get("id", ""), color=text_on_light)),
                        ft.DataCell(ft.Text(r.get("name", ""), color=text_on_light)),
                        ft.DataCell(ft.Text(r.get("kind", ""), color=text_on_light)),
                        ft.DataCell(ft.Text(r.get("subtype") or "", color=text_on_light)),
                        ft.DataCell(ft.Text(r.get("role") or "", color=text_on_light)),
                        ft.DataCell(ft.Text(", ".join(r.get("tags", [])), color=text_on_light)),
                        ft.DataCell(
                            ft.Row(
                                spacing=0,
                                controls=[
                                    ft.IconButton(
                                        icon=ft.Icons.EDIT,
                                        tooltip="Editar",
                                        icon_color=sec_color,
                                        on_click=lambda e, _r=r: open_resource_dialog(_r),
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE,
                                        tooltip="Eliminar",
                                        icon_color=ft.Colors.RED_400,
                                        on_click=lambda e, _id=r["id"]: delete_resource(_id),
                                    ),
                                ],
                            )
                        ),
                    ]
                )
            )

        # Tabla dentro de contenedor “pro”
        table_container = ft.Container(
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
        self.view.controls.append(table_container)
