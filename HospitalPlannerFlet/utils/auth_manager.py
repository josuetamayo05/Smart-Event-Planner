from __future__ import annotations
import json, os, hashlib, base64, secrets, hmac
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

    # Hashing seguro (PBKDF2)
    # Formato: pbkdf2$<iters>$<salt_b64>$<hash_b64>
    def _hash_pbkdf2(self, password: str, iterations: int = 180_000) -> str:
        salt = secrets.token_bytes(16)
        dk = hashlib.pbkdf2_hmac(
            "sha256",
            (password or "").encode("utf-8"),
            salt,
            iterations,
            dklen=32,
        )
        return "pbkdf2$%d$%s$%s" % (
            iterations,
            base64.b64encode(salt).decode("utf-8"),
            base64.b64encode(dk).decode("utf-8"),
        )

    def _verify_pbkdf2(self, password: str, stored: str) -> bool:
        try:
            _, iters_s, salt_b64, hash_b64 = stored.split("$", 3)
            iterations = int(iters_s)
            salt = base64.b64decode(salt_b64.encode("utf-8"))
            expected = base64.b64decode(hash_b64.encode("utf-8"))
            dk = hashlib.pbkdf2_hmac(
                "sha256",
                (password or "").encode("utf-8"),
                salt,
                iterations,
                dklen=len(expected),
            )
            return hmac.compare_digest(dk, expected)
        except Exception:
            return False

    # Legacy (tu SHA256 actual)
    def _hash_legacy_sha256(self, password: str) -> str:
        return hashlib.sha256((password or "").encode("utf-8")).hexdigest()

    def _is_legacy_sha256(self, s: str) -> bool:
        # 64 hex chars
        if not isinstance(s, str) or len(s) != 64:
            return False
        try:
            int(s, 16)
            return True
        except Exception:
            return False

    def _ensure_default_admin(self):
        if not self.data["users"]:
            # OJO: deja esto solo para primer arranque; ideal: forzar cambio luego.
            self.data["users"].append({
                "username": "admin",
                "password_hash": self._hash_pbkdf2("admin123"),  # ya seguro
                "role": "admin"
            })
            self._save()

    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        username = (username or "").strip().lower()

        changed = False
        for u in self.data["users"]:
            if u.get("username", "").strip().lower() != username:
                continue

            ph = u.get("password_hash", "")

            # Caso nuevo PBKDF2
            if isinstance(ph, str) and ph.startswith("pbkdf2$"):
                if self._verify_pbkdf2(password, ph):
                    return {"username": u["username"], "role": u.get("role", "staff")}
                return None

            # Caso legacy SHA256 (migra automáticamente si entra bien)
            if self._is_legacy_sha256(ph):
                if hmac.compare_digest(self._hash_legacy_sha256(password), ph):
                    u["password_hash"] = self._hash_pbkdf2(password)  # migración
                    changed = True
                    return {"username": u["username"], "role": u.get("role", "staff")}
                return None

            return None

        if changed:
            self._save()

        return None