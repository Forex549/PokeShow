import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Dict, List
from uuid import uuid4


_STORAGE_LOCK = Lock()
_STORAGE_PATH = Path(__file__).resolve().parents[3] / "data" / "storage.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _ensure_storage_file() -> None:
    if _STORAGE_PATH.exists():
        return
    _STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    data: Dict[str, object] = {"users": {}, "battles": {}}
    _STORAGE_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _read_storage() -> Dict[str, object]:
    _ensure_storage_file()
    raw = _STORAGE_PATH.read_text(encoding="utf-8")
    return json.loads(raw)


def _write_storage(data: Dict[str, object]) -> None:
    _STORAGE_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def create_user(username: str) -> Dict[str, object]:
    with _STORAGE_LOCK:
        data = _read_storage()
        users: Dict[str, Dict[str, object]] = data.get("users", {})

        user_id = str(uuid4())
        user = {
            "id": user_id,
            "username": username,
            "battles": [],
            "created_at": _utc_now(),
        }
        users[user_id] = user
        data["users"] = users
        _write_storage(data)
        return user


def get_user(user_id: str) -> Dict[str, object]:
    with _STORAGE_LOCK:
        data = _read_storage()
        users: Dict[str, Dict[str, object]] = data.get("users", {})
        if user_id not in users:
            raise KeyError(user_id)
        return users[user_id]


def add_user_battle(user_id: str, battle_id: str) -> None:
    with _STORAGE_LOCK:
        data = _read_storage()
        users: Dict[str, Dict[str, object]] = data.get("users", {})
        if user_id not in users:
            raise KeyError(user_id)
        battles: List[str] = list(users[user_id].get("battles", []))
        if battle_id not in battles:
            battles.append(battle_id)
        users[user_id]["battles"] = battles
        data["users"] = users
        _write_storage(data)


def save_battle_state(battle_id: str, user_id: str, state: Dict[str, object]) -> None:
    with _STORAGE_LOCK:
        data = _read_storage()
        battles: Dict[str, Dict[str, object]] = data.get("battles", {})
        now = _utc_now()
        entry = battles.get(battle_id, {})
        battles[battle_id] = {
            "id": battle_id,
            "user_id": user_id,
            "state": state,
            "created_at": entry.get("created_at", now),
            "updated_at": now,
        }
        data["battles"] = battles
        _write_storage(data)


def get_battle_state(battle_id: str) -> Dict[str, object]:
    with _STORAGE_LOCK:
        data = _read_storage()
        battles: Dict[str, Dict[str, object]] = data.get("battles", {})
        if battle_id not in battles:
            raise KeyError(battle_id)
        return battles[battle_id]


def list_user_battles(user_id: str) -> List[str]:
    user = get_user(user_id)
    return list(user.get("battles", []))
