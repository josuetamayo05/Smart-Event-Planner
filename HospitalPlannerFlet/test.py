from datetime import datetime
from uuid import uuid4

from models.database_manager import DatabaseManager
from models.scheduler import Scheduler
from models.event import Event

db = DatabaseManager("database.json")
sch = Scheduler(db)



# Evento 1 usa 1 unidad de CAMARA de 10:00 a 11:00
e1 = Event(
    id=str(uuid4()),
    name="Uso cámara A",
    description="",
    event_type="consulta_cardiologia",
    start=datetime(2026, 2, 1, 10, 0),
    end=datetime(2026, 2, 1, 11, 0),
    resource_ids=["CAMARA"],
    resource_units={"CAMARA": 1},
)
print("E1:", [v.code for v in sch.validate_event(e1)])
db.upsert_event(e1.to_dict())

# Evento 2 solapado usa 1 unidad (debe pasar porque qty=2)
e2 = Event(
    id=str(uuid4()),
    name="Uso cámara B",
    description="",
    event_type="consulta_cardiologia",
    start=datetime(2026, 2, 1, 10, 30),
    end=datetime(2026, 2, 1, 11, 30),
    resource_ids=["CAMARA"],
    resource_units={"CAMARA": 1},
)
print("E2:", [v.code for v in sch.validate_event(e2)])
db.upsert_event(e2.to_dict())

# Evento 3 solapado usa 1 unidad (debe FALLAR: 1+1+1 > 2)
e3 = Event(
    id=str(uuid4()),
    name="Uso cámara C (debe fallar)",
    description="",
    event_type="consulta_cardiologia",
    start=datetime(2026, 2, 1, 10, 45),
    end=datetime(2026, 2, 1, 11, 15),
    resource_ids=["CAMARA"],
    resource_units={"CAMARA": 1},
)
viol = sch.validate_event(e3)
print("E3:", [(v.code, v.message) for v in viol])

print("QTY:", sch._resource_quantity("CAMARA"))
print("REQ E1:", sch._requested_units(e1, "CAMARA"))
print("REQ E2:", sch._requested_units(e2, "CAMARA"))