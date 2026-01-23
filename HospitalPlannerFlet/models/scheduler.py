from __future__ import annotations
from dataclasses import dataclass
from collections import Counter
from datetime import datetime, timedelta
from typing import List, Iterable, Optional
from models.database_manager import DatabaseManager
from models.event import Event
from models.resource import Resource
from models.constraint import Violation

def overlaps(s1:datetime, e1:datetime, s2: datetime, e2:datetime) -> bool:
    return s1<e2 and s2<e1

def hhmm_to_minutes(hhmm:str)->int:
    h, m=hhmm.split(":")
    return int(h) * 60 + int(m)

WEEKDAY_KEYS = ["mon","tue","wed","thu","fri","sat","sun"]

@dataclass
class CandidateSlot:
    resources: List[Resource]
    start: datetime
    end: datetime

class Scheduler:
    def __init__(self, db: DatabaseManager):
        self.db = db

    #helpers

    def _all_resources(self) -> List[Resource]:
        return [Resource.from_dict(r) for r in self.db.list_resources()]

    def _all_events(self) -> List[Event]:
        return [Event.from_dict(r) for r in self.db.list_events()]

    def _resources_by_id(self, ids: Iterable[str]) -> List[Resource]:
        all_res={r.id: r for r in self._all_resources()}
        return [all_res[rid] for rid in ids if rid in all_res]
    
    def _requested_units(self, ev:Event, rid:str)-> int:
        if rid in ev.resource_units:
            return int(ev.resource_units.get(rid,0))
        return 1 if rid in ev.resource_ids else 0
    
    def _resource_quantity(self, rid: str)-> int:
        rmap= {r.id: r for r in self._all_resources()}
        r=rmap.get(rid)
        return int(getattr(r,"quantity",1) or 1)

    #  disponibilidad basica

    def _check_availability(self, event:Event)->List[Violation]:
        violations:List[Violation]=[]

        # Por simplicidad: no permitimos eventos que crucen medianoche
        if event.start.date()!=event.end.date():
            violations.append(
                Violation(
                    code="CROSSES_MIDNIGHT",
                    message="El evento no puede cruzar medianoche (start y end deben ser el mismo día)."
                )
            )
            return violations
        
        res_map = {r.id: r for r in self._all_resources()}

        day_key=WEEKDAY_KEYS[event.start.weekday()]
        start_min=event.start.hour *60+event.start.minute
        end_min=event.end.hour * 60 + event.end.minute
        
        relevant_ids=set(event.resource_ids)| set(event.resource_units.keys())

        for rid in relevant_ids:
            r=res_map.get(rid)
            if not r: continue

            availability = getattr(r, "availability", None)
            if not availability:
                continue

            weekly=availability.get("weekly",{})
            windows=weekly.get(day_key,[])

            # windows esperado: [["08:00","18:00"], ...]
            within_any_window=False
            for w in windows:
                if not isinstance(w,list) or len(w)!=2:
                    continue
                w_start=hhmm_to_minutes(w[0])
                w_end=hhmm_to_minutes(w[1])
                if start_min>=w_start and end_min<=w_end:
                    within_any_window=True
                    break

            if not within_any_window:
                violations.append(
                    Violation(
                        code="OUTSIDE_AVAILABILITY",
                        message=f"El recurso '{r.name}' no está disponible ese día/hora según tu turno."
                    )
                )
                # no seguimos con blackouts si ya está fuera
                continue

            # blackout    
            blackouts= availability.get("blackouts",[])
            for b in blackouts:
                try:
                    b_start=datetime.strptime(b["start"],"%Y-%m-%dT%H:%M")
                    b_end=datetime.strptime(b["end"],"%Y-%m-%dT%H:%M")
                except Exception:
                    continue

                if overlaps(event.start, event.end, b_start, b_end):
                    reason=b.get("reason","Bloqueo")
                    violations.append(
                        Violation(
                            code="RESOURCE_BLACKOUT",
                            message=f"El recurso '{r.name}' está bloqueado por: {reason}"
                        )
                    )
                    break
        
        return violations



    def is_resource_free(self, rid: str, start:datetime, end:datetime, req_units:int=1,
                         ignore_event_id:Optional[str]=None) -> bool:
        
        qty=self._resource_quantity(rid)
        used=0
        for other in self._all_events():
            if ignore_event_id and other.id==ignore_event_id:
                continue
            if overlaps(other.start,other.end, start, end):
                used+=self._requested_units(other,rid)
        return used+req_units<=qty
    

    def validate_event(self, event:Event) -> List[Violation]:
        violations:List[Violation]=[]

        #1 capacities
        violations.extend(self._check_resource_capacity(event))
        #2 co-requisitos
        violations.extend(self._check_corequisites(event))
        #3 exclusiones mutuas
        violations.extend(self._mutual_corequisites(event))
        #4 blackouts and avaibilitys
        violations.extend(self._check_availability(event))
        
        return violations
    
    # ---------- co-requisitos ----------

    def _check_resource_capacity(self,ev:Event)->List[Violation]:
        violations:List[Violation]=[]
        all_events=self._all_events()

        # conjunto de recursos relevantes (por ids seleccionados + resource_units)
        relevant_ids = set(ev.resource_ids) | set(ev.resource_units.keys())

        for rid in relevant_ids:
            qty = self._resource_quantity(rid)
            req = self._requested_units(ev,rid)
            if req<=0:continue 

            used=0
            for other in all_events:
                if other.id==ev.id:
                    continue
                if overlaps(other.start, other.end,ev.start,ev.end):
                    used+=self._requested_units(other, rid)
                
            if used+req>qty:
                violations.append(Violation(
                    code="RESOURCE_CAPACITY_EXCEEDED",
                    message=f"Recurso: '{rid}': ocupado {used}/{qty} unidades. Solicitadas {req} unidades."
                ))
        return violations


    def _check_corequisites(self, event: Event) -> List[Violation]:
        violations:List[Violation]=[]
        event_resources = self._resources_by_id(event.resource_ids)
        roles = Counter(r.role for r in event_resources if r.kind=="human")

        #Quirofano -> 1 cirujano, 1 anestesiologo, 2 enfermeras
        user_of=any(r.subtype=="quirofano" for r in event_resources)
        if user_of:
            required={"cirujano": 1, "anestesiologo": 1, "enfermera": 2}
            missing = {role: qty for role, qty in required.items() if roles.get(role, 0) < qty}
            if missing:
                detail=", ".join(f"{rol} x{qty}" for rol, qty in missing.items())
                violations.append(
                    Violation(
                        code="OR_COREQUISITES",
                        message=f"El quirófano requiere {detail}."))

        # Cirugia cardiaca -> cardiologo + equipo CEC
        if event.event_type == "cirugia_cardiaca":
            if roles.get("cardiologo",0)<1:
                violations.append(Violation(
                    code="CARDIO_SURGEON_MISSING",
                    message="La cirugía cardíaca requiere de un cardiólogo"))
            
            has_cec=any("cec" in (r.tags or []) for r in event_resources)
            if not has_cec:
                violations.append(
                    Violation(
                        code="CEC_MISSING",
                        message="La cirugía cardíaca requiere equipo de circulación extracorpórea (CEC).",
                ))

        return violations


    def _mutual_corequisites(self, event: Event) -> List[Violation]:
        violations:List[Violation]=[]
        event_resources = self._resources_by_id(event.resource_ids)
        all_events=self._all_events()

        def is_infectious_or(res_list: List[Resource])->bool:
            return any(r.subtype=="quirofano" and "infeccioso" in (r.tags or []) for r in res_list)
        
        def is_transplant(ev: Event, res_list:List[Resource])->bool:
            return (ev.event_type=="trasplante") or any("trasplante" in (r.tags or []) for r in res_list)
        
        day=event.start.date()
        this_inf=is_infectious_or(event_resources)
        this_tr=is_transplant(event,event_resources)
        
        if this_inf or this_tr:
            for other in all_events:
                if other.id==event.id:
                    continue
                if other.start.date()!=day:
                    continue
                other_res=self._resources_by_id(other.resource_ids)
                other_inf=is_infectious_or(other_res)
                other_tr=is_transplant(other, other_res)

                if (this_inf and other_tr) or (this_tr and other_inf):
                    violations.append(Violation(
                        code="INF_OR_VS_TRASPLANT",
                        message="No se permite quirófano infeccioso el mismo día que cirugías de trasplante."
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

                if (uses_ct and other_uses_rt) or (uses_rt and other_uses_ct):
                    violations.append(
                        Violation(
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
            {"roles": ["cardiologo"], "subtypes": ["quirofano"]}
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
            all_free=all(self.is_resource_free(r.id,current,end,req_units=1) for r in candidate_resources)
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
                    results.append(CandidateSlot(resources=candidate_resources, start=current, end=end))

            current+=step

        return results
    
    def find_next_slots_autofill(
            self,
            fixed_resource_ids:list[str],
            event_type:str,
            duration:timedelta,
            from_dt:datetime,
            max_results:int=3,
            search_horizon_days:int=30,
            step_minutes:int=15,
    )->List[CandidateSlot]:
        
        fixed_resources=self._resources_by_id(fixed_resource_ids)
        fixed_ids=[r.id for r in fixed_resources]

        # co-requisitos que se deben cumplir
        required_roles = Counter()
        uses_or=any(r.subtype=="quirofano" for r in fixed_resources)
        if uses_or:
            required_roles.update({"cirujano":1,"anestesiologo":1,"enfermera":2})

        required_cec = (event_type == "cirugia_cardiaca")
        step=timedelta(minutes=step_minutes)
        limit=from_dt+timedelta(days=search_horizon_days)

        all_resources=self._all_resources()

        def pick_free(role: str, qty: int, start: datetime, end: datetime) -> list[Resource]:
            candidates = [
                r for r in all_resources
                if r.kind == "human" and r.role == role and self.is_resource_free(r.id, start, end)
            ]
            return candidates[:qty]

        def pick_free_tag(tag: str, start: datetime, end: datetime) -> Optional[Resource]:
            candidates = [
                r for r in all_resources
                if r.kind == "physical" and tag in (r.tags or []) and self.is_resource_free(r.id, start, end)
            ]
            return candidates[0] if candidates else None
        
        results:List[CandidateSlot]=[]
        current=from_dt

        while current+duration <= limit and len(results)<max_results:
            end=current+duration

            # 1) fijos libres
            if not all(self.is_resource_free(rid,current, end, req_units=1) for rid in fixed_ids):
                current += step
                continue

            chosen: list[Resource] = list(fixed_resources)

            # 2) especiales por tipo
            if required_cec:
                cec = pick_free_tag("cec", current, end)
                if not cec:
                    current += step
                    continue
                chosen.append(cec)

                # además un cardiólogo
                required_roles.update({"cardiologo": 1})

            # 3) humanos requeridos
            ok = True
            for role, qty in required_roles.items():
                picked = pick_free(role, qty, current, end)
                if len(picked) < qty:
                    ok = False
                    break
                chosen.extend(picked)

            if not ok:
                current += step
                continue

            # 4) validar con tus mismas reglas (incluye exclusiones mutuas)
            dummy = Event(
                id="__dummy__",
                name="",
                description="",
                event_type=event_type,
                start=current,
                end=end,
                resource_ids=[r.id for r in chosen],
            )
            if not self.validate_event(dummy):
                results.append(CandidateSlot(resources=chosen, start=current, end=end))

            current += step
        
        return results
