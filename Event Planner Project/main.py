import tkinter as tk
from services.workes import Worker, Specialty, Shift
from ui.main_window import MainWindow
from models.Events.event import *
from models.date import Date
from datetime import time
import json
from services import *

def main():
    window=tk.Tk()
    MainWindow(window)

if __name__ == '__main__':
    help(tk)


