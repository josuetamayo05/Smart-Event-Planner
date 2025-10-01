from datetime import time
class Date:
    def __init__(self, description:str ,startDate:time, endDate:time):
        self.startDate = startDate
        self.endDate = endDate
        self.description = description