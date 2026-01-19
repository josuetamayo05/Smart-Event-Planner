import traceback
import faulthandler

# Si hay crash duro, a veces deja algo aquí
faulthandler.enable(open("faulthandler_dump.txt", "w"), all_threads=True)

from kivy.lang import Builder
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivymd.app import MDApp

# IMPORTS IMPORTANTES: fuerza a registrar clases de KivyMD usadas en KV
from kivymd.uix.navigationdrawer import MDNavigationLayout, MDNavigationDrawer  # noqa: F401
# from kivymd.uix.toolbar import MDTopAppBar  # noqa: F401
# from kivymd.uix.list import MDList, OneLineListItem  # noqa: F401
from kivymd.uix.boxlayout import MDBoxLayout  # noqa: F401
from kivymd.uix.label import MDLabel  # noqa: F401


KV = r"""
#:kivy 2.2.0
#:import dp kivy.metrics.dp
#:import MDScreen kivymd.uix.screen.MDScreen

<DashboardScreen@MDScreen>:
    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Dashboard"
            left_action_items: [["menu", lambda x: nav_drawer.set_state("toggle")]]

        MDLabel:
            text: "Frontend base OK"
            halign: "center"

MDNavigationLayout:
    ScreenManager:
        id: sm
        DashboardScreen:
            name: "dashboard"

    MDNavigationDrawer:
        id: nav_drawer
        MDBoxLayout:
            orientation: "vertical"
            padding: dp(12)
            spacing: dp(8)

            MDLabel:
                text: "Hospital"
                font_style: "H5"
                size_hint_y: None
                height: self.texture_size[1] + dp(10)

            MDList:
                OneLineListItem:
                    text: "Dashboard"
                    on_release:
                        sm.current = "dashboard"
                        nav_drawer.set_state("close")
"""


class T(MDApp):
    def build(self):
        try:
            return Builder.load_string(KV)
        except Exception:
            err = traceback.format_exc()
            print(err)
            return ScrollView(do_scroll_x=False, do_scroll_y=True, content=Label(text=err, text_size=(1000, None), size_hint_y=None))


if __name__ == "__main__":
    T().run()