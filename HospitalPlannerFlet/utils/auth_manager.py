from __future__ import annotations
import json, os, hashlib, base64
from typing import Optional, Dict, Any

class AuthManager:
    def __init__(self, path="users.json"):
        self.path = path
        self.data = {"users": []}
        self._load()
        self._ensure_default_admin()

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self._save()
        self.data.setdefault("users", [])

    def _save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def _hash(self, password: str) -> str:
        # simple hash (para proyecto). Si quieres PBKDF2 te lo paso.
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def _ensure_default_admin(self):
        if not self.data["users"]:
            self.data["users"].append({"username": "admin", "password_hash": self._hash("admin123"), "role": "admin"})
            self._save()

    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        username = (username or "").strip().lower()
        h = self._hash(password or "")
        for u in self.data["users"]:
            if u["username"].lower() == username and u["password_hash"] == h:
                return {"username": u["username"], "role": u.get("role", "staff")}
        return None