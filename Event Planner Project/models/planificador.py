from models.Events.event import Event
from datetime import time
from models.resource import Resource
from models.constraint import Constraint,MutualExclusionConstraint,CoRequirementConstraint

class Planificador:
    def __init__(self):
        self.list_event=[]
        self.list_resources=[]
        self.constraints=[]
        self.initial_hour=time(7,30)
        self.final_hour=time(19,0)
        self.workes=[]
        self.setup_hospital_constraints()

    def setup_hospital_constraints(self):
        self.constraints.append(CoRequirementConstraint("Quirófano 1 - Cardiovascular", "Cirujano Cardiovascular"))
        self.constraints.append(CoRequirementConstraint("Quirófano 1 - Cardiovascular", "Perfusionista"))
        self.constraints.append(CoRequirementConstraint("Quirófano 2 - Neurocirugía", "Neurocirujano"))
        self.constraints.append(CoRequirementConstraint("Quirófano 3 - Ortopedia", "Cirujano Ortopédico"))
        self.constraints.append(CoRequirementConstraint("Quirófano 4 - General", "Cirujano General"))
        #Anestesia
        self.constraints.append(CoRequirementConstraint("Anestesia General", "Anestesiólogo"))
        self.constraints.append(CoRequirementConstraint("Anestesia General", "Enfermero Anestesista"))
        self.constraints.append(CoRequirementConstraint("Anestesia Pediátrica", "Anestesiólogo Pediátrico"))
        #Equipos Especializados
        self.constraints.append(
            CoRequirementConstraint("Máquina de Circulación Extracorpórea", "Perfusionista Certificado"))
        self.constraints.append(CoRequirementConstraint("Ventilador de Alta Frecuencia", "Terapeuta Respiratorio"))
        self.constraints.append(CoRequirementConstraint("Monitor de Presión Intracraneal", "Enfermero de Neuro-UCI"))

        # IMAGENOLOGÍA
        self.constraints.append(CoRequirementConstraint("Resonancia Magnética 1.5T", "Técnico en RMN Nivel II"))
        self.constraints.append(CoRequirementConstraint("Angiógrafo", "Radiólogo Intervencionista"))
        self.constraints.append(CoRequirementConstraint("Ecógrafo Doppler", "Ecografista Certificado"))

        # UNIDADES ESPECIALES
        self.constraints.append(CoRequirementConstraint("Sala de Partos", "Ginecólogo"))
        self.constraints.append(CoRequirementConstraint("Sala de Partos", "Enfermero Obstetra"))
        self.constraints.append(CoRequirementConstraint("UCI Neonatal", "Neonatólogo"))
        self.constraints.append(CoRequirementConstraint("UCI Adultos", "Médico Intensivista"))
        self.constraints.append(CoRequirementConstraint("Sala de Hemodiálisis", "Enfermero de Diálisis"))

        #Exclusiones
        # SEGURIDAD CON EQUIPOS
        self.constraints.append(MutualExclusionConstraint("Resonancia Magnética", "Marcapasos"))
        self.constraints.append(MutualExclusionConstraint("Resonancia Magnética", "Clips Aneurisma Metálicos"))
        self.constraints.append(MutualExclusionConstraint("Tomografía con Contraste", "Insuficiencia Renal Aguda"))
        self.constraints.append(MutualExclusionConstraint("Radioterapia", "Embarazo Confirmado"))

        # CONFLICTOS DE ESPACIO
        self.constraints.append(MutualExclusionConstraint("Quirófano 1 - Cardiovascular", "Quirófano 2 - Neurocirugía"))
        self.constraints.append(MutualExclusionConstraint("Sala de Endoscopía", "Sala de Broncoscopía"))
        self.constraints.append(MutualExclusionConstraint("Cama UCI", "Cama de Hospitalización Regular"))

        # CONFLICTOS DE PERSONAL
        self.constraints.append(MutualExclusionConstraint("Dr. García - Cirujano", "Dra. López - Cirujano"))
        self.constraints.append(MutualExclusionConstraint("Enfermero UCI Turno Mañana", "Enfermero UCI Turno Tarde"))

        # CONFLICTOS DE PROCEDIMIENTOS
        self.constraints.append(MutualExclusionConstraint("Anticoagulación Terapéutica", "Biopsia Percutánea"))
        self.constraints.append(MutualExclusionConstraint("Radiación Ionizante", "Mujer Embarazada"))
        self.constraints.append(MutualExclusionConstraint("Estudio con Bario", "Estudio con Yodo"))



    def add_event(self,event:Event):
        if event.start_event<self.initial_hour or event.end_event>self.final_hour:
            raise ValueError(f"❌ Error: el horario del hospital está entre {self.initial_hour} y {self.final_hour}")

        self.list_event.append(event)

    def add_resource_to_event(self,resource:Resource,event:Event):
        if resource.is_used:
            raise ValueError("El objeto está siendo usado para otra función")
        self.list_resources.append(resource)


