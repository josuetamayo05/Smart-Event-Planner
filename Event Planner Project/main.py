import tkinter as tk
from ui.main_window import MainWindow
from core.event_manager import EventManager
from models.date import Date
from datetime import time
import json
from services.personal_gestor import PersonalGestor
def main():
    s=PersonalGestor()
    s.create_example()


if __name__ == '__main__':
    main()