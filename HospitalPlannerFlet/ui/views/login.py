from __future__ import annotations
import flet as ft

from ui.design import prime_color, light_color, white_color, sec_color


class LoginView:
    def __init__(self, page: ft.Page, auth_manager, on_success):
        self.page = page
        self.auth = auth_manager
        self.on_success = on_success

        CARD_W = 420
        CARD_H = 520
        FIELD_W = 320

        # Campos
        self.loginfield = ft.TextField(
            label="Usuario",
            hint_text="Escribe tu usuario",
            width=FIELD_W,
            border_color=prime_color,
            color="black",
        )

        self.passfield = ft.TextField(
            label="Contraseña",
            hint_text="Escribe tu contraseña",
            width=FIELD_W,
            border_color=prime_color,
            color="black",
            password=True,
            can_reveal_password=True,
        )

        self.enterText = ft.Text(" ", size=0, weight=ft.FontWeight.BOLD)

        def do_login(e):
            user = self.auth.authenticate(self.loginfield.value or "", self.passfield.value or "")
            if user:
                self.enterText.value = "¡Bienvenido!"
                self.enterText.size = 16
                self.enterText.color = ft.Colors.GREEN
                self.page.update()
                self.on_success(user)
            else:
                self.enterText.value = "Datos incorrectos"
                self.enterText.size = 16
                self.enterText.color = ft.Colors.RED
                self.page.update()

        # Header compacto
        mainIcon = ft.Icon(ft.Icons.LOCAL_HOSPITAL, color=prime_color, size=44)
        mainText = ft.Text("Iniciar sesión", size=22, weight=ft.FontWeight.BOLD, color=prime_color)
        subText = ft.Text("Acceso para personal autorizado", size=12, color=ft.Colors.GREY_700)

        accept = ft.ElevatedButton(
            "Entrar",
            bgcolor=prime_color,
            color=light_color,
            width=260,
            height=44,
            on_click=do_login,
        )

        # Columna interior (más compacta)
        mainColumn = ft.Column(
            controls=[
                mainIcon,
                mainText,
                subText,
                ft.Divider(height=6, color=ft.Colors.TRANSPARENT),
                self.loginfield,
                self.passfield,
                accept,
                self.enterText,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,  # más pequeño que antes
        )

        # Card suave
        card = ft.Container(
            width=CARD_W,
            height=CARD_H,
            padding=20,
            border_radius=18,
            bgcolor=white_color if "white_color" in globals() else light_color,
            border=ft.border.all(1, ft.Colors.with_opacity(0.12, ft.Colors.BLACK)),
            alignment=ft.alignment.Alignment(0, 0),
            content=mainColumn,
        )
        card.shadow = ft.BoxShadow(
            blur_radius=24,
            spread_radius=1,
            color=ft.Colors.with_opacity(0.12, ft.Colors.BLACK),
            offset=ft.Offset(0, 8),
        )

        # Contenedor raíz centrado (clave para centralizar)
        self.view = ft.Container(
            expand=True,
            bgcolor=sec_color if "sec_color" in globals() else light_color,  # fondo ventana
            alignment=ft.alignment.Alignment(0, 0),
            content=card,
        )