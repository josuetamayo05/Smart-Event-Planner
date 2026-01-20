from __future__ import annotations
import json
import os
import shutil
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional

DEFAULT_DB: Dict[str,Any]={
    "resources":[],
    "events":[],
    "constraints":{
        "corequisites":[],
        "mutual_exclusions":[],
    },
}

class DatabaseManager:
    def __init__(self,path: str="database.json"):
        self.path=path
        self._lock=threading.RLock()
        self.data:Dict[str,Any]={}
        self.load()
        
    def load(self)->None:
        with self._lock:
            if os.path.exists(self.path):
                with open(self.path,"r",encoding="utf-8") as f:
                    self.data=json.load(f)
            else:
                self.data=DEFAULT_DB.copy()
                self.save()

            self.data.setdefault("resources",[])
            self.data.setdefault("events",[])
            self.data.setdefault("constraints",{"corequisites":[],"mutual_exclusions":[]})
            self.data["constraints"].setdefault("corequisites",[])
            self.data["constraints"].setdefault("mutual_exclusions",[])

    def save(self)->None:
        """Guardado atómico para evitar corrupción si se corta el proceso."""
        with self._lock:
            folder=os.path.dirname(self.path) or "."
            os.makedirs(folder,exist_ok=True)

            tmp_path=self.path+".tmp"
            with open(tmp_path,"w",encoding="utf-8") as f:
                json.dump(self.data,f,ensure_ascii=False,indent=2)

            os.replace(tmp_path,self.path)
    
    def save_async(self)->None:
        threading.Thread(target=self.save,daemon=True).start()


    # ---------- backup / import / export
    def backup(self,folder:str="backups")->str:
        with self._lock:
            os.makedirs(folder,exist_ok=True)
            ts=datetime.now().strftime("%Y%m%d_%H%M%S")
            dst=os.path.join(folder,f"database_{ts}.json")
            shutil.copy2(self.path,dst)
            return dst
        
    def export_to(self,path:str)->None:
        with self._lock:
            with open(path,"w",encoding="utf-8") as f:
                json.dump(self.data,f,ensure_ascii=False,indent=2)

    def import_from(self,path:str)->None:
        with self._lock:
            with open(path,"r",encoding="utf-8") as f:
                self.data=json.load(f)
            self.save()

    # ---------- Resources ----------

    def list_resources(self)->List[Dict[str,Any]]:
        return list(self.data.get("resources",[]))
    
    def upsert_resource(self, resource_dict: Dict[str, Any]) -> None:
        with self._lock:
            resources = self.data.setdefault("resources", [])
            rid = resource_dict.get("id")
            if not rid:
                raise ValueError("El recurso debe tener 'id'.")

            for i, r in enumerate(resources):
                if r.get("id") == rid:
                    resources[i] = resource_dict
                    break
            else:
                resources.append(resource_dict)

            self.save_async()
    
    def delete_resource(self,resource_id:str)->None:
        with self._lock:
            resources=self.data.setdefault("resources",[])
            self.data["resources"]=[r for r in resources if r.get("id")!=resource_id]
            self.save_async()
    
    # ---------- Events ----------
    def list_events(self)->List[Dict[str,Any]]:
        return list(self.data.get("events",[]))
    
    def get_event(self,event_id:str)->Optional[Dict[str,Any]]:
        for e in self.data.get("events",[]):
            if e.get("id")==event_id:   
                return e
        return None
    
    def upsert_event(self,event_dict:Dict[str,Any])->None:
        """
        event_dict esperado:
        {
          "id": "...",
          "name": "...",
          "description": "...",
          "event_type": "...",
          "start": "YYYY-MM-DDTHH:MM",
          "end": "YYYY-MM-DDTHH:MM",
          "resource_ids": [...]
        }
        """
        with self._lock:
            events=self.data.setdefault("events",[])
            eid=event_dict.get("id")
            if not eid:
                raise ValueError("El evento debe tener 'id'.")
            
            for i, e in enumerate(events):
                if e.get("id")==eid:
                    events[i]=event_dict
                    break
            else:
                events.append(event_dict)

            self.save_async()

    def delete_event(self,event_id:str)->None:
        with self._lock:
            events=self.data.setdefault("events",[])
            self.data["events"]=[e for e in events if e.get("id")!=event_id]
            self.save_async()
    