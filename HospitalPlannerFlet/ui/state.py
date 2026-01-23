from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date

@dataclass
class AppState:
    selected_index:int=0
    selected_resource_ids: set[str] = field(default_factory=set)

    calendar_date:date=field(default_factory=date.today)
    resource_filter:str="" #"" =todos
    resource_units: dict[str,int]=field(default_factory=dict)