from __future__ import annotations
from datetime import datetime

def parse_dt(date_str:str,time_str: str) -> datetime:
    d= datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
    t=datetime.strptime(time_str.strip(),"%H:%M").time()
    return  datetime.combine(d,t)
