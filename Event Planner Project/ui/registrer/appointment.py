import tkinter.messagebox
from _datetime import datetime
from tkinter.ttk import *
import sqlite3
from unittest import result
from tkcalendar import Calendar
import tkinter as tk
from tkinter import *
import os
from ui.principal_window import principal_menu

db_path = '../../data/database.db'
os.makedirs(os.path.dirname(db_path), exist_ok=True)  # Crear directorio si no existe

conn = sqlite3.connect(db_path)
c = conn.cursor()

# Crear la tabla si no existe
c.execute('''
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        location TEXT NOT NULL,
        phone TEXT NOT NULL,
        events TEXT NOT NULL,
        date TEXT NOT NULL,
        genner TEXT NOT NULL
    )
''')
conn.commit()
ids=[]

class MainWindow:
    def __init__(self,root):
        self.root=root
        self.root.title("Sistema de Gestion Hospitalaria")
        self.left=Frame(root, width=800, height=720,bg='white')
        self.left.pack(side=LEFT)
        self.right=Frame(root, width=400, height=720,bg='steelblue')
        self.right.pack(side=RIGHT)


        self.heading=Label(self.left,text="Registro del Paciente",font=('arial 30 bold'),fg='black',bg='white')
        self.heading.place(x=30,y=0)

        ## LABEls for the windows
        self.name=Label(self.left,text="Nombre del Paciente",font=('arial 12 bold'),fg='black',bg='white')
        self.name.place(x=30,y=105)

        self.age=Label(self.left,text="Edad",font=('arial 12 bold'),fg='black',bg='white')
        self.age.place(x=30,y=140)

        self.location=Label(self.left,text="Dirección",font=('arial 12 bold'),fg='black',bg='white')
        self.location.place(x=30,y=175)

        self.number=Label(self.left,text="Número de teléfono",font=('arial 12 bold'),fg='black',bg='white')
        self.number.place(x=30,y=210)

        self.events=Label(self.left,text="Tipo de Consulta",font=('arial 12 bold'),fg='black',bg='white')
        self.events.place(x=29,y=245)

        self.day=Label(self.left,text="Fecha", font=('arial 12 bold'),fg='black',bg='white')
        self.day.place(x=31,y=280)

        self.genner=Label(self.left,text="Género",font=('arial 12 bold'),fg='black',bg='white')
        self.genner.place(x=31,y=350)

        ## Entry all labels
        self.name_ent=Entry(self.left,width=80)
        self.name_ent.place(x=250,y=110)

        self.age_ent=Entry(self.left,width=80)
        self.age_ent.place(x=250,y=145)

        self.location_ent=Entry(self.left,width=80)
        self.location_ent.place(x=250,y=180)

        self.phone_ent=Entry(self.left,width=80)
        self.phone_ent.place(x=250,y=215)

        self.events = [
            "Anestesiología",
            "Cirugía General",
            "Pediatría",
            "Medicina Interna",
            "Cardiología",
            "Ginecología y Obstetricia",
            "Traumatología",
            "Ortopedia",
            "Dermatología",
            "Oftalmología",
            "Otorrinolaringología",
            "Neurología",
            "Neurocirugía",
            "Urología",
            "Nefrología",
            "Endocrinología",
            "Gastroenterología",
            "Neumología",
            "Oncología",
            "Hematología",
            "Reumatología",
            "Alergología",
            "Infectología",
            "Psiquiatría",
            "Psicología Clínica",
            "Radiología",
            "Medicina Nuclear",
            "Patología",
            "Medicina Familiar",
            "Medicina de Urgencias",
            "Cuidados Intensivos",
            "Medicina Física y Rehabilitación",
            "Geriatría",
            "Odontología",
            "Cirugía Plástica",
            "Cirugía Cardiovascular",
            "Cirugía Torácica",
            "Cirugía Maxilofacial",
            "Cirugía Pediátrica",
            "Angiología",
            "Flebología",
            "Mastología",
            "Fertilidad",
            "Nutriología",
            "Oncología Radioterápica",
            "Medicina del Trabajo",
            "Medicina del Deporte",
            "Genética Médica",
            "Paliativos",
            "Laboratorio Clínico",
            "Banco de Sangre",
            "Farmacia Hospitalaria",
            "Enfermería",
            "Terapia Respiratoria",
            "Fisioterapia",
            "Terapia Ocupacional",
            "Logopedia",
            "Audiología",
            "Optometría",
            "Podología",
            "Nutrición Enteral",
            "Vacunación",
            "Control Prenatal",
            "Control del Niño Sano",
            "Chequeo Médico General",
            "Medicina Preventiva",
            "Salud Pública",
            "Epidemiología",
            "Medicina Tropical"
        ]

        self.combo_events=Combobox(self.left,values=self.events)
        self.combo_events.place(x=250,y=250)

        self.date_ent = Entry(self.left, width=80)
        self.date_ent.place(x=250, y=285)

        self.genners=["Masculino","Femenino"]
        self.combo_gen=Combobox(self.left,values=self.genners)
        self.combo_gen.place(x=250,y=350)

        def select_date():
            def get_date():
                date_sel=cal.get_date()
                self.date_ent.delete(0,END)
                self.date_ent.insert(0,date_sel)
                top.destroy()
            actual_date=datetime.now()

            top = Toplevel(self.root)
            top.title("Seleccionar Fecha")
            top.geometry("400x300")
            cal = Calendar(top, selectmode='day', year=2025, month=actual_date.month, day=actual_date.day)
            cal.pack(pady=10, padx=10)

            buttom_conf=Button(top,text="Confirmar Calendario",command=get_date)
            buttom_conf.pack(padx=10)

        ## Buttoms
        self.button_calendar = Button(self.left, text="Abrir Calendario", command=select_date)
        self.button_calendar.place(x=250, y=310)

        self.submit=Button(self.left,text="Agregar Datos", font=('arial 12 bold'),fg='black',bg='white',command=self.add_data,height=1,width=20)
        self.submit.place(x=40, y=450)

        self.out_but=Button(self.left,text="Volver",font=('arial 12 bold'), fg='black',bg='white',command=self.out_window,height=1,width=20)
        self.out_but.place(x=350, y=450)
        # getting the number of appointments fixed to view in the log
        sql2="SELECT COUNT(*) FROM appointments "
        self.result=c.execute(sql2)
        for self.row in self.result:
            self.count=self.row[0]
            ## self.id=self.row[0]
            ## ids.append(self.id)

        # ordering ids
        if ids:
            self.new=sorted(ids)
            self.final_id=self.new[len(ids)-1]
        else:
            self.final_id=0
        ## displaying the logs in our right frame
        self.logs=Label(self.right,text="Registros",font=('arial 20 bold'),fg='white',bg='steelblue')
        self.logs.place(x=20,y=0)

        self.box=Text(self.right,width=40,height=30)
        self.box.place(x=20,y=60)
        self.box.insert(END,"Total inscripciones:  " + str(self.count))

        self.root.mainloop()

    def out_window(self):
        self.root.destroy()
        principal_menu.init()

    def add_data(self):
        self.val1=self.name_ent.get()
        try:
            self.val2=int(self.age_ent.get())
        except ValueError:
            tkinter.messagebox.showerror("Error", "Edad incorrecta")
        self.val2=self.age_ent.get()
        self.val3=self.location_ent.get()
        self.val4=self.phone_ent.get()
        self.val5=self.combo_events.get()
        self.val6=self.date_ent.get()
        self.val7=self.combo_gen.get()

        if self.val1=='' or self.val2=='' or self.val3=='' or self.val4=='' or self.val5=='' or self.val6=='' or self.val7=='':
            tkinter.messagebox.showerror("Error","Por favor rellene todos los datos seleccionados")
        # elif not self.val4.isdigit():
        #     tkinter.messagebox.showerror("Error","El número de teléfono debe ser un dígito")
        # elif 0>int(self.val2) or int(self.val2) > 120:
        #     tkinter.messagebox.showerror("Error", "Edad incorrecta")
        # elif not self.val2.isdigit():
        #     tkinter.messagebox.showerror("Error", "La edad debe ser un dígito")
        # elif len(self.val4)<8:
        #     tkinter.messagebox.showerror("Error","El Número de teléfono debe temer al menos 8 digitos")
        # # elif not self.valid_date(self.val6):
        # #     tkinter.messagebox.showerror("Error","Debes rellenar correctamente la fecha")
        # elif not self.val7 in self.genners:
        #     tkinter.messagebox.showerror("Error","Debes rellenar correctamente el género")
        # elif not self.val5 in self.combo_events:
        #     tkinter.messagebox.showerror("Error","Tipo de Consulta no encontrada")

        ## Add to Database
        else:
            sql="INSERT INTO 'appointments' (name, age, location, phone, events, date, genner) VALUES (?, ?, ?, ?, ?, ?, ?)"
            c.execute(sql,(self.val1, self.val2, self.val3, self.val4, self.val5, self.val6, self.val7))
            conn.commit()
            tkinter.messagebox.showinfo("Success", f"Datos agregados correctamente para {self.val1}")

            self.box.insert(END,' Cita fijada para ' + self.val1 + ' a las  ' + self.val6)

    def valid_date(self, str_date)->bool:
        try:
            date_obj = datetime.strptime(str_date, "%d/%m/%Y")
            return True
        except ValueError:
            return False


def init():
    root = Tk()
    wind = MainWindow(root)
    root.geometry("1200x720+0+0")
    root.resizable(0, 0)
    root.mainloop()

# init()

