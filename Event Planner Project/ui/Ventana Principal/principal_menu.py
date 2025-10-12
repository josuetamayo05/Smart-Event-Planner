from tkinter import *
from PIL import ImageTk, Image
from tkinter.ttk import *
import tkinter.messagebox

class menu_principal:
    def __init__(self, master):
        self.master=master
        self.master.title("Sistema de Gestion Hospitalaria")
        self.master.geometry("1200x720+0+0")
        self.master.resizable(0,0)
        self.master.state("zoomed")
        self.master.title("Login Page")

        self.bg_frame=Image.open('../../images/hospital1.jpeg')
        photo=ImageTk.PhotoImage(self.bg_frame)
        self.bg_panel=Label(self.master,image=photo)
        self.bg_panel.image = photo
        self.bg_panel.pack(fill='both', expand='yes')

        # Login Frame
        
        self.lgn_frame=Frame(self.master,width=950,height=600,bg='black') ## SolutionedErrorr
        self.lgn_frame.place(x=200,y=70)

        heading=Label(self.lgn_frame,text="Hospital General",font=('yu gothic ui', 25, "bold"),bg="#9AECF5", fg='black',
                      bd=5,relief=FLAT)
        heading.place(x=80, y=30, width=500, height=45)


wind=Tk()
window=menu_principal(wind)

wind.mainloop()

