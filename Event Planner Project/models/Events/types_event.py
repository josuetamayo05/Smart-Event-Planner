from enum import Enum
from datetime import time
class TypeEvent(Enum):
    CIRUGIA_PLASTICA={
        "nombre": "Cirugía Plástica",
        "duración": time(2,0),
        "recursos_tipicos": ["Cirujano Plastico", "Quirofano"]
    }
