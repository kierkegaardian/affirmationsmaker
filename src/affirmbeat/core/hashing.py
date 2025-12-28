from __future__ import annotations

import hashlib
import json
from typing import Any


def stable_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def hash_dict(obj: dict[str, Any]) -> str:
    payload = stable_json(obj).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
