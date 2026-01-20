from __future__ import annotations
import flet as ft

def snack(page: ft.Page,msg:str):
    page.snack_bar=ft.SnackBar(ft.Text(msg))
    page.snack_bar.open=True
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