import flet as ft
print([x for x in dir(ft.Icons) if "DASH" in x or "HOME" in x or "EVENT" in x][:200])