from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_report(directory: Path, report: dict[str, Any]) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "processing_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [f"{key}: {json.dumps(value, ensure_ascii=False)}" for key, value in report.items()]
    (directory / "processing_report.txt").write_text("\n".join(lines), encoding="utf-8")

