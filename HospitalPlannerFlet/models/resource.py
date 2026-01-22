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
    quantity:int=1

    @classmethod
    def from_dict(cls, data: dict) -> "Resource":
        return cls(
            id=data["id"],
            name=data["name"],
            kind=data.get("kind","physical"),
            subtype=data.get("subtype"),
            role=data.get("role"),
            tags=data.get("tags",[]),
            availability=data.get("availability"),
            quantity=int(data.get("quantity",1))
        )

    def to_dict(self) -> dict:
        d= {
            "id": self.id,
            "name": self.name,
            "kind": self.kind,
            "subtype": self.subtype,
            "role": self.role,
            "tags": self.tags,
            "quantity": int(self.quantity or 1),
        }
        if self.availability is not None:
            d["availability"]=self.availability
        
        return d