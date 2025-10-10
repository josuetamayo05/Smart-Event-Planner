from enum import Enum

class Resource:
    def __init__(self, id, name, description):
        self.is_used=False
        self.id=id
        self.name=name
        self.description=description


