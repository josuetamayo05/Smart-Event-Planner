from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock
from kivymd.app import MDApp



class HospitalApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #Backend: database+controller
        self.db=Data


if __name__ == '__main__':
    print_hi('PyCharm')

