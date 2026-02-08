from __future__ import annotations
from datetime import datetime

def parse_dt(date_str:str,time_str: str) -> datetime:
    d= datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
    t=datetime.strptime(time_str.strip(),"%H:%M").time()
    return  datetime.combine(d,t)

def sum_one_day(date_str:str):
    temp=date_str.split("-")

    

if __name__=="__main__":
    print(datetime)