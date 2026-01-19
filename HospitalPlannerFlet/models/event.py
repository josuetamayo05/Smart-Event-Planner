from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import List

ISO_FMT="%Y-%m-%dT%H:%M"

@dataclass
class Event:
    id: str
    name: str
    description: str
    event_type: str
    start: datetime
    end: datetime
    resource_ids: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "Event":
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description",""),
            event_type=data.get("event_type",""),
            start=datetime.strptime(data["start"],ISO_FMT),
            end=datetime.strptime(data["end"],ISO_FMT),
            resource_ids=data.get("resource_ids",[]),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "event_type": self.event_type,
            "start": self.start.strftime(ISO_FMT),
            "end": self.end.strftime(ISO_FMT),
            "resource_ids": self.resource_ids,
        }