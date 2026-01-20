from __future__ import annotations
import flet as ft
from ui.dialogs import snack, open_dialog, close_dialog

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

            id_tf = ft.TextField(label="ID", value=(existing.get("id") if is_edit else ""))
            name_tf = ft.TextField(label="Nombre", value=(existing.get("name") if is_edit else ""))
            kind_dd = ft.Dropdown(
                label="Kind",
                options=[ft.dropdown.Option("physical"), ft.dropdown.Option("human")],
                value=(existing.get("kind") if is_edit else "physical"),
            )
            subtype_tf = ft.TextField(label="Subtype (si physical)", value=(existing.get("subtype") if is_edit else ""))
            role_tf = ft.TextField(label="Role (si human)", value=(existing.get("role") if is_edit else ""))
            tags_tf = ft.TextField(label="Tags (coma)", value=",".join(existing.get("tags", [])) if is_edit else "")

            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("Editar recurso" if is_edit else "Nuevo recurso"),
                content=ft.Column([id_tf, name_tf, kind_dd, subtype_tf, role_tf, tags_tf],
                                  tight=True, scroll=ft.ScrollMode.AUTO, height=360),
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
                if is_edit and rid != existing["id"]:
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
                    "subtype": (subtype_tf.value or "").strip() or None,
                    "role": (role_tf.value or "").strip() or None,
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