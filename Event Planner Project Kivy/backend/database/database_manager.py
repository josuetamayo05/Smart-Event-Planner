from __future__ import annotations
import json
import os
from threading import Thread
from typing import Any, Dict, List
from datetime import datetime

DEFAULT_DB={
    "resource":[],
    "events":[],
    "constraints":{
        "corequisites":[],
        "mutual_exclusions":[],
    },
}

class DatabaseManager:
    def __init__(self, path: str="database.json"):
        self.path=path
        self.data:Dict[str, Any]={}
        self.load()

    def load(self)->None:
        if os.path.exists(self.path):
            with open(self.path,"r",encoding="utf-8") as f:
                self.data=json.load(f)
        else:
            self.data=DEFAULT_DB
            self.save()

    def save(self)->None:
        os.makedirs(os.path.dirname(self.path) or ".",exist_ok=True)
        with open(self.path,"w",encoding="utf-8") as f:
            json.dump(self.data,f,ensure_ascii=False,indent=2)

    def save_async(self)->None:
        Thread(target=self.save,daemon=True).start()

    # helpers CRUD
    def list_resources(self)->List[Dict[str,Any]]:
        return self.data.get("resources",[])

    def list_events(self)->List[Dict[str,Any]]:
        return self.data.get("events",[])

    def upsert_event(self,event_dict:Dict[str,Any]) -> None:
        events=self.data.setdefault("events",[])
        for idx, ev in enumerate(events):
            if ev["id"]==event_dict["id"]:
                events[idx]=event_dict
                break
            else:
                events.append(event_dict)
            self.save_async()

    def delete_event(self,event_id:str) -> None:
        events=self.data.setdefault("events",[])
        self.data["events"]=[e for e in events if e["id"]!=event_id]
        self.save_async()

    # export/ import/ backup
    def export_to(self,path:str)->None:
        with open(path,"w",encoding="utf-8") as f:
            json.dump(self.data,f,ensure_ascii=False,indent=2)

    def import_from(self, path:str)->None:
        with open(path,"r",encoding="utf-8") as f:
            self.data=json.load(f)
        self.save_async()

    def backup(self,folder:str="backups")->str:
        os.makedirs(folder,exist_ok=True)
        ts=datetime.now().strftime("%Y%m%d%H%M%S")
        backup_path=os.path.join(folder,f"database_{ts}.json")
        self.export_to(backup_path)

