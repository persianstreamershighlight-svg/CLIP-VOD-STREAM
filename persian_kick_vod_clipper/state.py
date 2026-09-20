from __future__ import annotations

import json
from pathlib import Path


class ProcessingState:
    def __init__(self, path: Path):
        self.path = path
        self.data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"completed": []}

    def done(self, stage: str) -> bool:
        return stage in self.data["completed"]

    def complete(self, stage: str) -> None:
        if stage not in self.data["completed"]:
            self.data["completed"].append(stage)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")

