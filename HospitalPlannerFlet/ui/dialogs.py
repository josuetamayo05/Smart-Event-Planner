from __future__ import annotations
import flet as ft

_snack_ref = {}
def snack(page: ft.Page, msg: str, error: bool = False):
    sb = _snack_ref.get(id(page))
    if sb is None:
        sb = ft.SnackBar(
            ft.Text("", color=ft.Colors.WHITE),
            bgcolor=ft.Colors.BLACK87,
        )
        page.overlay.append(sb)
        _snack_ref[id(page)] = sb
    sb.content.value = msg
    sb.bgcolor = ft.Colors.RED_600 if error else ft.Colors.BLACK87
    sb.open = True
    page.update()

def open_dialog(page: ft.Page, dlg: ft.AlertDialog):
    if dlg not in page.overlay:
        page.overlay.append(dlg)
    dlg.open=True
    page.update()

def close_dialog(page:ft.Page, dlg: ft.AlertDialog):
    dlg.open=False
    page.update()

def show_dialog(page: ft.Page, title:str, body:str):
    dlg=ft.AlertDialog(
        modal=True,
        title=ft.Text(title),
        content=ft.Text(body),
    )
    dlg.actions=[ft.TextButton("OK", on_click=lambda e:close_dialog(page,dlg))]
    open_dialog(page,dlg)