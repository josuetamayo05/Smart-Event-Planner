from tkinter import *
from tkinter import ttk
import sqlite3
import tkinter.messagebox

conn=sqlite3.connect('../../data/database.db')
cursor=conn.cursor()

class Update:
    def __init__(self,master):
        self.master=master
        self.left=Frame(master,width=800,height=720,bg='white')
        self.left.pack(side=LEFT)

        self.right=Frame(master,width=400,height=720,bg='steelblue')
        self.right.pack(side=RIGHT)

        self.heading=Label(self.left,text="Modificar Citas",fg='steelblue',font=('arial 40 bold'))
        self.heading.place(x=150,y=10)

        self.name=Label(self.left,text="Introduzca nombre del paciente a buscar",font=('arial 12 bold'))
        self.name.place(x=150,y=150)

        self.name_entry=Entry(self.left,width=50)
        self.name_entry.place(x=150,y=200)

        self.search_buttom=Button(self.left, text="Buscar", command=self.search_db)
        self.search_buttom.place(x=150,y=250)

    def search_db(self):
        self.input=self.name_entry.get()
        top=Toplevel(self.left)
        top.geometry('800x600')
        head=Label(top,text="Base de Datos",fg='steelblue',font=('arial 40 bold'))
        head.place(x=150,y=0)
        #executue sql
        sql="SELECT * FROM appointments WHERE name LIKE ?"
        self.res=cursor.execute(sql,(self.input,))
        for self.row in self.res:
            self.name=self.row[1]
            self.age=self.row[2]
            self.direction=self.row[3]
            self.number_phone=self.row[4]
            self.consult=self.row[5]
            self.date=self.row[6]
            self.genner=self.row[7]

        # create updateform
        self.uname=Label(top,text="Nombre del paciente", font=('arial 12 bold'))
        self.uname.place(x=40,y=140)

        self.uage=Label(top,text="Edad",font=('arial 12 bold'))
        self.uage.place(x=40,y=175)

        self.udirection=Label(top,text="Dirección",font=('arial 12 bold'))
        self.udirection.place(x=40,y=210)

        self.unumber=Label(top,text="Número de teléfono", font=('arial 12 bold'))
        self.unumber.place(x=40,y=245)

        self.uconsult=Label(top,text="Consulta",font=('arial 12 bold'))
        self.uconsult.place(x=40,y=280)

        self.udate=Label(top,text="Fecha de la Cita",font=('arial 12 bold'))
        self.udate.place(x=40,y=315)

        self.ugenner=Label(top,text="Género", font=('arial 12 bold'))
        self.ugenner.place(x=40,y=350)

        #entry bottoms labels
        self.ent1=Entry(top,width=50)
        self.ent1.place(x=300,y=140)
        self.ent1.insert(END,str(self.name))

        self.ent2=Entry(top,width=50)
        self.ent2.place(x=300,y=175)
        self.ent2.insert(END,str(self.age))

        self.ent3=Entry(top,width=50)
        self.ent3.place(x=300,y=210)
        self.ent3.insert(END,str(self.direction))

        self.ent4=Entry(top,width=50)
        self.ent4.place(x=300,y=245)
        self.ent4.insert(END,str(self.number_phone))

        self.ent5=Entry(top,width=50)
        self.ent5.place(x=300,y=280)
        self.ent5.insert(END,str(self.consult))

        self.ent6=Entry(top,width=50)
        self.ent6.place(x=300,y=315)
        self.ent6.insert(END,str(self.date))

        self.ent7=Entry(top,width=50)
        self.ent7.place(x=300,y=350)
        self.ent7.insert(END,str(self.genner))

        #buttons execute delete or update
        self.update_btn=Button(top,text="Modificar",width=20,height=2,bg='lightblue',command=self.update_db)
        self.update_btn.place(x=400,y=380)

        self.delete_btn=Button(top,text="Eliminar",width=20,height=2,bg='lightblue',command=self.delete_db)
        self.delete_btn.place(x=150,y=380)

    def update_db(self):
        self.var1=self.ent1.get()
        self.var2=self.ent2.get()
        self.var3=self.ent3.get()
        self.var4=self.ent4.get()
        self.var5=self.ent5.get()
        self.var6=self.ent6.get()
        self.var7=self.ent7.get()

        query="UPDATE appointments SET name=?, age=?, location=?, phone=?, events=?, date=?, genner=? WHERE name LIKE ?"
        cursor.execute(query,(self.var1,self.var2,self.var3,self.var4,self.var5,self.var6,self.var7))
        conn.commit()
        tkinter.messagebox.showinfo("Modificado","Modificación Completa")

    def delete_db(self):
        sql2="DELETE FROM appointments WHERE name LIKE ?"
        cursor.execute(sql2,(self.name,))
        conn.commit()
        tkinter.messagebox.showinfo("Eliminado","Eliminado con éxito")
        self.ent1.destroy()
        self.ent2.destroy()
        self.ent3.destroy()
        self.ent4.destroy()
        self.ent5.destroy()
        self.ent6.destroy()
        self.ent7.destroy()


update=Tk()
wind=Update(update)
update.geometry("1200x720+0+0")
update.resizable(False, False)
update.mainloop()
