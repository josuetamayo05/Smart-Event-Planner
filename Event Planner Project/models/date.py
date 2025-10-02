from datetime import time
class Date:
    def __init__(self, pacient_name:str, description:str ,start_date:time, end_date:time):
        self.start_date = start_date
        self.end_date = end_date
        self.description = description
        self.pacient_name = pacient_name




