import json
from services.workes import Worker,Shift,Specialty
from datetime import time
import os

class PersonalGestor:
    def __init__(self, archive_data="data/personal.json"):
        self.archive_data = archive_data
        self.workes=[]
        self.loading_data()
        self.save_data()
        self._ensure_data_directory()

    def loading_data(self):
        try:
            with open(self.archive_data,"r",encoding='utf-8') as f:
                data = json.load(f)
                self.workes = data['workes']
        except FileNotFoundError:
            self.workes=[]

    def save_data(self):
        data=[self.worker_to_dict(t) for t in self.workes]
        with open(self.archive_data,"w",encoding='utf-8') as f:
            json.dump(data,f,indent=2,ensure_ascii=False)

    def add_worker(self,name:str, specialty:Specialty,shift:Shift,work_shedule:tuple):
        worker=Worker(name,specialty,shift,work_shedule)
        self.workes.append(worker)
        self.save_data()
        return worker

    def search_workes_specialty(self,_specialty:Specialty):
        return [worker for worker in self.workes if worker.specialty == _specialty]

    def search_available_workes_specialty(self,specialty:Specialty,start,end):
        specialtys=self.search_workes_specialty(specialty)
        return [worker for worker in specialtys if worker.isAvailable(start,end)]

    def worker_to_dict(self,worker:Worker):
        """Convierte objeto Trabajador a dict para JSON"""
        return {
            "nombre":worker.name,
            "specialty":worker.specialty.value,
            "shift":worker.shift.value,
            "horario_trabajo":[worker.work_schedule[0].strftime("%H:%M"),
                               worker.work_schedule[1].strftime("%H:%M")],
            "disponible":worker.available
        }
    def dict_to_worker(self,data):
        shedule=(
            time.fromisoformat(data["horario_trabajo"][0]),
            time.fromisoformat(data["horario_trabajo"][1])
        )
        specialty=Specialty(data["specialty"])
        shift=Shift(data["shift"])
        return Worker(data["nombre"],specialty,shift,shedule)

    def create_example(self):
        workes_example = [
            self.add_worker("Raul", Specialty.ENFERMERO, Shift.MATUTINO, (time(7, 0), time(15, 0))),
            self.add_worker("Jesus", Specialty.ENFERMERO, Shift.VESPERTINO, (time(12, 0), time(20, 0))),
            self.add_worker("Joshua", Specialty.CIRUJANO, Shift.MATUTINO, (time(8, 0), time(16, 0))),
        ]
        self.save_data()

if __name__ == "__main__":
    personal=PersonalGestor()
    personal.create_example()