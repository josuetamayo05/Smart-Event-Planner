from __future__ import annotations
from dataclasses import dataclass, field
from typing import List,Optional,Dict,Any

@dataclass
class Resource:
    id: str
    name: str
    kind: str
    subtype: str | None = None
    role: str | None = None
    tags:List[str] = field(default_factory=list)
    availability:Optional[Dict[str,Any]]=None

    @classmethod
    def from_dict(cls, data: dict) -> "Resource":
        return cls(
            id=data["id"],
            name=data["name"],
            kind=data.get("kind","physical"),
            subtype=data.get("subtype"),
            role=data.get("role"),
            tags=data.get("tags",[]),
            availability=data.get("availability")
        )

    def to_dict(self) -> dict:
        d= {
            "id": self.id,
            "name": self.name,
            "kind": self.kind,
            "subtype": self.subtype,
            "role": self.role,
            "tags": self.tags,
        }
        if self.availability is not None:
            d["availability"]=self.availability
        
        return d