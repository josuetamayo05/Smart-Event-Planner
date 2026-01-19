from dataclasses import dataclass

@dataclass
class Violation:
    code:str
    message:str
    severity:str="error"
    