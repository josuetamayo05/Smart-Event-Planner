from __future__ import annotations
from dataclasses import dataclass
from collections import Counter
from datetime import datetime, timedelta
from typing import List, Iterable, Optional
from backend.database.database_manager import DatabaseManager
from event import Event
from resource import Resource
from constraint import Violation

def overlaps(s1:datetime, e1:datetime, s2: datetime, e2:datetime) -> bool:
    return s1<e2 and s2<e1

@dataclass
class CandidateSlot:
    resources: List[Resource]
    start: datetime
    end: datetime

class Sheduler:
    def __init__(self, db: DatabaseManager):
        self.db = db

    #helpers

    def _all_resources(self) -> List[Resource]:
        return [Resource.from_dict(r) for r in self.db.list_resources()]

    def _all_events(self) -> List[Event]:
        return [Event.from_dict(r) for r in self.db.list_events()]

    def _resources_by_id(self, ids: Iterable[str]) -> List[Resource]:
        all_res = {r.id for r in self._all_resources()}
        return [all_res[i] for i in ids if i in all_res]

    #  disponibilidad basica
    def is_resource_free(self, resource_id: str, start:datetime, end:datetime,
                         ignore_event_id:Optional[str]=None) -> bool:
        for ev in self._all_events():
            if ignore_event_id and ev.id == ignore_event_id:
                continue
            if resource_id in ev.resource_ids and overlaps(ev.start, ev.end, start,end):
                return False
        return True

    def validate_event(self, event:Event) -> List[Violation]:
        violations:List[Violation]=[]
        for rid in event.resource_ids:
            #1 recursos no solapados
            if not self.is_resource_free(rid, event.start, event.end, ignore_event_id=event.id):
                res= next((r for r in self._all_resources() if r.id== rid), None)
                name=res.name if res else rid
                violations.append(Violation(
                    code="RESOURCE_OVERLAP",
                    message=f'El recurso {name} ya está ocupado en ese horario',
                ))

            #2 co-requisitos
            violations.extend(self._check_corequisites(event))

            #3 exclusiones mutuas
            violations.extend(self._mutual_corequisites(event))

    def _check_corequisites(self, event: Event) -> List[Violation]:
        violations:List[Violation]=[]
        event_resources = self._resources_by_id(event.resource_ids)
        roles = Counter(r.role for r in event_resources if r.kind=="human")

        #Quirofano -> 1 cirujano, 1 anestesiologo, 2 enfermeras
        user_of=any(r.subtype=="quirófano" for r in event_resources)
        if user_of:
            required={"cirujano": 1, "anestesiologo": 1, "enfermera": 2}
            missing={
                role: qty for role, qty in required.items()
                if roles.get(role,0)<qty
            }
            if missing:
                detail=", ".join(f"{rol} x{qty}" for rol, qty in missing.items())
                violations.append(Violation(code="OR_COREQUISITES", message=f'El quirófano requiere {detail}.'))

        # Cirugia cardiaca -> cardiologo + equipo CEC
        if event.event_type == "cirugia_cardiaca":
            if roles.get("cirujano",0)<1:
                violations.append(Violation(
                    code="CARDIO_SURGEON_MISSING",
                    message="La cirugía cardíaca requiere de un cardiólogo"))

        return violations


    def _check_mutual_corequisites(self, event: Event) -> List[Violation]:
        violations:List[Violation]=[]
        event_resources = self._resources_by_id(event.resource_ids)
        all_events=self._all_events()

        # Quirófano infeccioso vs trasplante el mismo día
        uses_infectious_or=any(r.subtype=="quirófano" and "infeccioso" in (r.tags or [])
                               for r in event_resources)
        if uses_infectious_or:
            day=event.start.date()
            for other in all_events:
                if other.id==event.id:
                    continue
                if other.start.date()!=day:
                    continue
                other_res=self._resources_by_id(other.resource_ids)
                is_transplant=(any("trasplante" in (r.tags or []) for r in other_res)
                               or other.event_type == "trasplante")
                if is_transplant:
                    violations.append(Violation(
                        code="INF_OR_VS_TRASPLANT",
                        message="El quirófano infeccioso no puede usarse el mismo día que cirugías de trasplante.",
                    ))
                    break

        # tomografo vs radioterapia solapados
        uses_ct=any(r.subtype=="tomografo" for r in event_resources)
        uses_rt=any(r.subtype in ("radioterapia", "acelerador_lineal") for r in event_resources)
        if uses_rt or uses_ct:
            for other in all_events:
                if other.id==event.id:
                    continue
                if not overlaps(other.start, other.end, event.start, event.end):
                    continue
                other_res=self._resources_by_id(other.resource_ids)
                other_uses_ct=any(r.subtype=="tomografo" for r in other_res)
                other_uses_rt=any(r.subtype in ("radioterapia","acelerador_lineal") for r in other_res)
                if (uses_rt and other_uses_ct) or (uses_rt and other_uses_ct):
                    violations.append(Violation(
                        code="CT_VS_RADIOTHERAPY",
                        message="El tomógrafo no puede usarse simultáneamente con terapia de radiación."
                    ))
                    break

        return violations


    # BUSQUEDA INTELIGENTE DE HUECOS
    def find_next_slots(
            self,
            required_filters:dict,
            duration:timedelta,
            from_dt:datetime,
            max_results:int=3,
            search_horizon_days:int=30,
            step_minutes:int=15,
    )->List[CandidateSlot]:
        """
        required_filters: dict con filtros sobre recursos, ej:
            {"roles": ["cardiologo"], "subtypes": ["quirófano"]}
        """
        roles=set(required_filters.get("roles",[]))
        subtypes=set(required_filters.get("subtypes",[]))
        resources=self._all_resources()

        def matches(r:Resource)->bool:
            ok_role=not roles or (r.role in roles)
            ok_sub=not subtypes or (r.subtype in subtypes)
            return ok_role and ok_sub
        candidate_resources=[r for r in resources if matches(r)]
        if not candidate_resources:
            return []
        results: List[CandidateSlot] = []
        step=timedelta(minutes=step_minutes)
        limit=from_dt+timedelta(days=search_horizon_days)

        current=from_dt
        while current + duration <= limit and len(results) < max_results:
            end=current + duration
            #todos los recursos filtro deben estar libres
            all_free=all(self.is_resource_free(r.id,current,end) for r in candidate_resources)
            if all_free:
                dummy=Event(
                    id="__dummy__",
                    name="",
                    description="",
                    event_type="",
                    start=current,
                    end=end,
                    resource_ids=[r.id for r in candidate_resources],
                )
                if not self.validate_event(dummy):
                    results.append(CandidateSlot(
                    start=current,
                    end=end,
                    resources=candidate_resources,
                    ))
            current+=step

        return results