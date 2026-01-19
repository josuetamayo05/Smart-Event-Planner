from kivy.lang import Builder
from kivymd.app import MDApp

# IMPORTS “forzados” para registrar clases (evita Unknown class <...> en KV)
from kivymd.uix.appbar import MDTopAppBar  # noqa
from kivymd.uix.navigationdrawer import MDNavigationLayout, MDNavigationDrawer  # noqa
from kivymd.uix.list import MDListItem, MDListItemHeadlineText  # noqa


KV = """
MDScreen:
    MDNavigationLayout:

        ScreenManager:
            id: sm

            MDScreen:
                name: "dashboard"
                MDBoxLayout:
                    orientation: "vertical"

                    MDTopAppBar:
                        title: "Dashboard"
                        left_action_items: [["menu", lambda x: nav_drawer.set_state("toggle")]]

                    MDLabel:
                        text: "UI OK"
                        halign: "center"

            MDScreen:
                name: "events"
                MDBoxLayout:
                    orientation: "vertical"

                    MDTopAppBar:
                        title: "Eventos"
                        left_action_items: [["menu", lambda x: nav_drawer.set_state("toggle")]]

                    MDLabel:
                        text: "Eventos OK"
                        halign: "center"

        MDNavigationDrawer:
            id: nav_drawer

            MDBoxLayout:
                orientation: "vertical"
                padding: "12dp"
                spacing: "8dp"

                MDLabel:
                    text: "Hospital"
                    font_style: "H5"
                    size_hint_y: None
                    height: self.texture_size[1] + dp(10)

                MDList:
                    MDListItem:
                        on_release:
                            sm.current = "dashboard"
                            nav_drawer.set_state("close")
                        MDListItemHeadlineText:
                            text: "Dashboard"

                    MDListItem:
                        on_release:
                            sm.current = "events"
                            nav_drawer.set_state("close")
                        MDListItemHeadlineText:
                            text: "Eventos"
"""


class HospitalApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        return Builder.load_string(KV)


if __name__ == "__main__":
    HospitalApp().run()