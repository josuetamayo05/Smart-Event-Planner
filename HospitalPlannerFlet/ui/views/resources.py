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

            kind_dd = ft.Dropdown(
                label="Kind",
                options=[ft.dropdown.Option("physical", "physical"), ft.dropdown.Option("human", "human")],
                value=(existing.get("kind") if is_edit else "physical"),
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

            tags_tf = ft.TextField(
                label="Tags (coma)",
                value=",".join(existing.get("tags", [])) if is_edit else "",
            )

            # Habilitar/deshabilitar según kind
            def apply_kind_state():
                if kind_dd.value == "physical":
                    subtype_dd.disabled = False
                    role_dd.disabled = True
                    role_dd.value = None
                else:
                    subtype_dd.disabled = True
                    subtype_dd.value = None
                    role_dd.disabled = False

            def on_kind_change(e):
                apply_kind_state()
                self.page.update()

            kind_dd.on_change = on_kind_change
            apply_kind_state()

            # Botón catálogo (rellena subtype o role según kind)
            def open_resource_catalog(_):
                kind = kind_dd.value
                items = RESOURCE_CATALOG["Físicos (subtype)"] if kind == "physical" else RESOURCE_CATALOG["Humanos (role)"]

                def pick(it: dict):
                    if kind == "physical":
                        subtype_dd.value = it["code"]
                    else:
                        role_dd.value = it["code"]
                    close_dialog(self.page, cat_dlg)
                    self.page.update()

                cat_dlg = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Catálogo de tipos de recurso"),
                    content=ft.Container(
                        width=520,
                        height=520,
                        content=ft.Column(
                            [
                                ft.ListTile(
                                    title=ft.Text(it["label"]),
                                    on_click=lambda e, it=it: pick(it),
                                )
                                for it in items
                            ],
                            scroll=ft.ScrollMode.AUTO,
                        ),
                    ),
                    actions=[ft.TextButton("Cerrar", on_click=lambda e: close_dialog(self.page, cat_dlg))],
                )
                open_dialog(self.page, cat_dlg)

            catalog_btn = ft.ElevatedButton("Mostrar catálogo", on_click=open_resource_catalog)

            # Diálogo
            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("Editar recurso" if is_edit else "Nuevo recurso"),
                content=ft.Column(
                    [
                        id_tf,
                        name_tf,
                        kind_dd,
                        ft.Row([ft.Container(subtype_dd, expand=True), catalog_btn]),
                        ft.Row([ft.Container(role_dd, expand=True), catalog_btn]),
                        tags_tf,
                    ],
                    tight=True,
                    scroll=ft.ScrollMode.AUTO,
                    height=420,
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

                tags = [t.strip() for t in (tags_tf.value or "").split(",") if t.strip()]

                self.db.upsert_resource({
                    "id": rid,
                    "name": rname,
                    "kind": kind_dd.value,
                    "subtype": subtype_dd.value if kind_dd.value == "physical" else None,
                    "role": role_dd.value if kind_dd.value == "human" else None,
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