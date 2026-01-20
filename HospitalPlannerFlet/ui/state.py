from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date

@dataclass
class AppState:
    selected_index=0
    selected_resource_ids: set[str] = field(default_factory=set)

    calendar_date:date=date.today()
    resource_filter:str="" #"" =todos