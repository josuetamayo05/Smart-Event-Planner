from __future__ import annotations
import flet as ft
from datetime import datetime, timedelta
from ui.design import prime_color, light_color, white_color, sec_color


class LoginView:
    def __init__(self, page: ft.Page, auth_manager, on_success):
        self.page = page
        self.auth = auth_manager
        self.on_success = on_success

        CARD_W = 460
        CARD_H = 540
        FIELD_W = 340

        # --- Seguridad/UX: bloqueo por intentos fallidos (solo UI/flujo, no cambia tu auth) ---
        self.failed_attempts = 0
        self.locked_until: datetime | None = None

        # --- Recordar usuario (solo usuario; nunca contraseña) ---
        saved_user = ""
        try:
            saved_user = self.page.client_storage.get("saved_user") or ""
        except Exception:
            saved_user = ""

        # Campos (diseño consistente con otras pantallas)
        self.loginfield = ft.TextField(
            label="Usuario",
            hint_text="Escribe tu usuario",
            width=FIELD_W,
            border_color=prime_color,
            color="black",
            bgcolor=ft.Colors.WHITE,
            filled=True,
            border_radius=14,
            prefix_icon=ft.Icons.PERSON_OUTLINE,
            autofocus=True,
            value=saved_user,
        )

        self.passfield = ft.TextField(
            label="Contraseña",
            hint_text="Escribe tu contraseña",
            width=FIELD_W,
            border_color=prime_color,
            color="black",
            bgcolor=ft.Colors.WHITE,
            filled=True,
            border_radius=14,
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            password=True,
            can_reveal_password=True,
        )

        # Enter en contraseña -> login (PC friendly)
        self.passfield.on_submit = lambda e: do_login(e)

        # Mensajería
        self.enterText = ft.Text(" ", size=0, weight=ft.FontWeight.BOLD)

        # Checkbox recordar
        self.remember_cb = ft.Checkbox(
            label="Recordar usuario",
            value=True if saved_user else False
        )

        # Loading (para evitar doble click y dar sensación pro)
        self.loading_ring = ft.ProgressRing(width=18, height=18, stroke_width=2, visible=False)

        def set_loading(is_loading: bool):
            self.loading_ring.visible = is_loading
            self.accept_btn.disabled = is_loading
            self.loginfield.disabled = is_loading
            self.passfield.disabled = is_loading
            self.page.update()

        def set_msg(text: str, color, size: int = 14):
            self.enterText.value = text
            self.enterText.size = size
            self.enterText.color = color
            self.page.update()

        def do_login(e):
            # Bloqueo temporal
            if self.locked_until and datetime.now() < self.locked_until:
                remaining = int((self.locked_until - datetime.now()).total_seconds())
                set_msg(f"Bloqueado temporalmente. Intenta en {remaining}s.", ft.Colors.RED, 14)
                return

            u = (self.loginfield.value or "").strip()
            p = (self.passfield.value or "").strip()

            if not u or not p:
                set_msg("Completa usuario y contraseña.", ft.Colors.RED, 14)
                return

            set_loading(True)

            try:
                user = self.auth.authenticate(u, p)
            except Exception:
                user = None

            set_loading(False)

            if user:
                # Reset intentos
                self.failed_attempts = 0
                self.locked_until = None

                # Guardar usuario si corresponde (solo username)
                try:
                    if self.remember_cb.value:
                        self.page.client_storage.set("saved_user", u)
                    else:
                        self.page.client_storage.remove("saved_user")
                except Exception:
                    pass

                set_msg("¡Bienvenido!", ft.Colors.GREEN, 16)

                # Limpia password por seguridad antes de continuar (opcional pero recomendado)
                self.passfield.value = ""
                # Revisar mala optimizacion entre page.update y on_succes, on succces podria ir 1ro
                self.on_success(user)
                self.page.update()

            else:
                self.failed_attempts += 1

                # Limpia contraseña para reintento rápido (PC)
                self.passfield.value = ""
                self.page.update()

                # Bloqueo tras 5 intentos
                if self.failed_attempts >= 5:
                    self.failed_attempts = 0
                    self.locked_until = datetime.now() + timedelta(seconds=45)
                    set_msg("Demasiados intentos. Bloqueado 45s.", ft.Colors.RED, 14)
                    return

                set_msg("Usuario o contraseña incorrectos.", ft.Colors.RED, 14)

        # Header compacto (pero con estilo pro)
        header = ft.Container(
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
                                content=ft.Icon(ft.Icons.LOCAL_HOSPITAL, color=prime_color, size=24),
                            ),
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text("Iniciar sesión", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                    ft.Text("Acceso para personal autorizado", size=13, color=ft.Colors.with_opacity(0.92, ft.Colors.WHITE)),
                                ],
                            ),
                        ],
                    ),
                    ft.Container(
                        padding=10,
                        border_radius=16,
                        bgcolor=ft.Colors.with_opacity(0.18, ft.Colors.WHITE),
                        border=ft.border.all(1, ft.Colors.with_opacity(0.22, ft.Colors.WHITE)),
                        content=ft.Icon(ft.Icons.SECURITY, color=ft.Colors.WHITE, size=22),
                    ),
                ],
            ),
        )

        # Botón Entrar (con loading al lado)
        self.accept_btn = ft.ElevatedButton(
            "Entrar",
            bgcolor=prime_color,
            color=light_color,
            width=260,
            height=44,
            on_click=do_login,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=14),
                padding=ft.padding.symmetric(horizontal=16, vertical=12),
            ),
        )

        # Columna interior (más compacta)
        mainColumn = ft.Column(
            controls=[
                header,
                ft.Divider(height=8, color=ft.Colors.TRANSPARENT),
                self.loginfield,
                self.passfield,
                ft.Row(
                    width=FIELD_W,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        self.remember_cb,
                        ft.Row(spacing=10, controls=[self.loading_ring]),
                    ],
                ),
                self.accept_btn,
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
            padding=18,
            border_radius=18,
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, ft.Colors.with_opacity(0.12, ft.Colors.BLACK)),
            alignment=ft.Alignment(0, 0),
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
            bgcolor=ft.Colors.with_opacity(0.12, sec_color),  # fondo ventana (suave)
            alignment=ft.Alignment(0, 0),
            content=card,
        )