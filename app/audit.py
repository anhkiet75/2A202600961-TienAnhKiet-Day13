from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

AUDIT_PATH = Path(os.getenv("AUDIT_LOG_PATH", "data/audit.jsonl"))


def audit(
    action: str,
    actor: str,
    outcome: str,
    **details: Any,
) -> None:
    """Write a single structured audit entry to the separate audit log."""
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "actor": actor,
        "outcome": outcome,
        **details,
    }
    with AUDIT_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
