from tkinter import *
from PIL import ImageTk, Image
import tkinter.messagebox
from ui.registrer import appointment
from ui.registrer import update


class menu_principal:
    def __init__(self, master):
        self.master=master
        self.master.resizable(0,0)
        self.master.state("zoomed")
        self.master.title("Login Page")

        bg_frame=Image.open('../../images/hospital1.jpeg')
        photo=ImageTk.PhotoImage(bg_frame)
        self.bg_panel=Label(self.master,image=photo)
        self.bg_panel.image = photo
        self.bg_panel.pack(fill='both', expand='yes')

        # Login Frame

        self.lgn_frame=Frame(self.master,width=950,height=580,bg='#150220') ## SolutionedErrorr
        self.lgn_frame.place(x=200,y=70)

        self.heading=Label(self.lgn_frame,text="Hospital General",font=('yu gothic ui', 25, "bold"),bg="#9AECF5", fg='black',
                bd=5,relief=FLAT)
        self.heading.place(x=80, y=30, width=500, height=45)

        side_img=Image.open('../../images/hospt.png')
        photo=ImageTk.PhotoImage(side_img)
        side_img=side_img.resize((400,400))
        side_img_label=Label(self.lgn_frame,image=photo,bg='#150220')
        side_img_label.image=photo
        side_img_label.place(x=130,y=150)

        ## Data Entry
        lgn_button=Image.open('../../images/btn1.png')
        photo=ImageTk.PhotoImage(lgn_button)
        lgn_button_label=Label(self.lgn_frame,image=photo,bg='#150220')
        lgn_button_label.image=photo
        lgn_button_label.place(x=550,y=150)
        login = Button(lgn_button_label, text='DATA ENTRY', font=("yu gothic ui", 13, "bold"), width=25, bd=0,
                       bg='#3047ff', cursor='hand2', activebackground='#3047ff', fg='white', command=self.update_db)

        login.place(x=20, y=10)

        ## Appointment
        lgn_button=Image.open('../../images/btn1.png')
        photo=ImageTk.PhotoImage(lgn_button)
        lgn_button_label_=Label(self.lgn_frame,image=photo,bg='#150220')
        lgn_button_label_.image=photo
        lgn_button_label_.place(x=550, y=250)
        login=Button(lgn_button_label_, text='APPOINTMENT', font=("yu gothic ui", 13, "bold"), width=25, bd=0,
                                bg='#3047ff', cursor='hand2', activebackground='#3047ff', fg='white',command=self.appointment)
        login.place(x=20, y=10)


        #Sign Out
        lgn_button = Image.open('../../images/btn1.png')
        photo = ImageTk.PhotoImage(lgn_button)
        lgn_button_label_ = Label(self.lgn_frame, image=photo, bg='#150220')
        lgn_button_label_.image = photo
        lgn_button_label_.place(x=550, y=350)
        login = Button(lgn_button_label_, text='SIGN OUT', font=("yu gothic ui", 13, "bold"), width=25, bd=0,
                       bg='#3047ff', cursor='hand2', activebackground='#3047ff', fg='white', command=self.sign_out)
        login.place(x=20, y=10)


    def update_db(self):
        self.master.destroy()
        update.init()
    def appointment(self):
        self.master.destroy()
        appointment.init()
    def sign_out(self):
        self.master.destroy()

def init():
    root = Tk()
    wind = menu_principal(root)
    root.geometry("1200x720+0+0")
    root.resizable(0, 0)
    root.mainloop()
