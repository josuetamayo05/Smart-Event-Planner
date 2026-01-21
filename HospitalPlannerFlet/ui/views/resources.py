from __future__ import annotations
import flet as ft
from ui.dialogs import snack, open_dialog, close_dialog
from ui.catalogs.resource_types import RESOURCE_CATALOG

class ResourcesView:
    def __init__(self, page: ft.Page, db):
        self.page = page
        self.db = db
        self.view = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)

    def refresh(self):
        self.view.controls.clear()
        self.view.controls.append(ft.Text("Recursos", size=22, weight=ft.FontWeight.BOLD))

        resources = sorted(self.db.list_resources(), key=lambda r: r.get("name", ""))

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
            self.db.delete_resource(rid)
            snack(self.page, "Recurso eliminado.")
            self.refresh()
            self.page.update()

        def open_resource_dialog(existing: dict | None = None):
            is_edit = existing is not None
            existing = existing or {}

            # Catálogos
            subtype_options = [
                ft.dropdown.Option(it["code"], it["label"])
                for it in RESOURCE_CATALOG["Físicos (subtype)"]
            ]
            role_options = [
                ft.dropdown.Option(it["code"], it["label"])
                for it in RESOURCE_CATALOG["Humanos (role)"]
            ]

            # Campos base
            id_tf = ft.TextField(label="ID", value=(existing.get("id", "") if is_edit else ""))
            name_tf = ft.TextField(label="Nombre", value=(existing.get("name", "") if is_edit else ""))

            # Kind: RADIO (más confiable que Dropdown dentro de dialog)
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

            existing_tags = set(existing.get("tags", [])) if is_edit else set()

            tag_options = RESOURCE_CATALOG.get("Tags sugeridos", [])
            tag_checks_col = ft.Column(spacing=2)

            def rebuild_tag_checks():
                tag_checks_col.controls.clear()
                for t in tag_options:
                    code = t["code"]
                    label = t["label"]

                    def on_tag_change(e, _code=code):
                        if e.control.value:
                            existing_tags.add(_code)
                        else:
                            existing_tags.discard(_code)

                    tag_checks_col.controls.append(
                        ft.Checkbox(label=label, value=(code in existing_tags), on_change=on_tag_change)
                    )

            rebuild_tag_checks()

            custom_tags_tf = ft.TextField(
                label="Tags extra (coma) (opcional)",
                value="",
                hint_text="Ej: esteril, pediatrico",
            )

            # Botones catálogo (dos instancias)
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
                                ft.ListTile(title=ft.Text(it["label"]),
                                            on_click=lambda e, it=it: pick(it))
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
                                ft.ListTile(title=ft.Text(it["label"]),
                                            on_click=lambda e, it=it: pick(it))
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
                else:
                    role_dd.value = None

                if update_ui:
                    subtype_dd.update()
                    role_dd.update()
                    subtype_row.update()
                    role_row.update()

            def on_kind_change(e):
                # debug
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
                        subtype_row,
                        role_row,
                        ft.Text("Tags sugeridos"),
                        ft.Container(
                            tag_checks_col,
                            border=ft.border.all(1, ft.Colors.GREY_300),
                            padding=10,
                            height=140,
                        ),
                        custom_tags_tf,
                    ],
                    tight=True,
                    scroll=ft.ScrollMode.AUTO,
                    height=460,
                ),
                actions=[],
            )

            def on_save(_):
                rid = (id_tf.value or "").strip()
                rname = (name_tf.value or "").strip()
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
                    return

                extra = [t.strip() for t in (custom_tags_tf.value or "").split(",") if t.strip()]
                tags = sorted(set(existing_tags).union(extra))

                self.db.upsert_resource({
                    "id": rid,
                    "name": rname,
                    "kind": kind_rg.value,
                    "subtype": subtype_dd.value if kind_rg.value == "physical" else None,
                    "role": role_dd.value if kind_rg.value == "human" else None,
                    "tags": tags,
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

        self.view.controls.append(
            ft.Row(
                [
                    ft.ElevatedButton("Nuevo recurso", on_click=lambda e: open_resource_dialog(None)),
                    ft.Text("Ej: quirofano => kind=physical, subtype='quirofano'", italic=True),
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
                                    ft.IconButton(icon=ft.Icons.EDIT, tooltip="Editar",
                                                  on_click=lambda e, _r=r: open_resource_dialog(_r)),
                                    ft.IconButton(icon=ft.Icons.DELETE, tooltip="Eliminar",
                                                  on_click=lambda e, _id=r["id"]: delete_resource(_id)),
                                ],
                                spacing=0,
                            )
                        ),
                    ]
                )
            )

        self.view.controls.append(table)