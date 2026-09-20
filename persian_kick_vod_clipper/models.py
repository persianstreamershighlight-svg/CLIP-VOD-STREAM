from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal


@dataclass(frozen=True)
class Segment:
    start: float
    end: float
    text: str


@dataclass(frozen=True)
class Rule:
    id: str
    title: str
    definition: str
    document_evidence: str
    decision: Literal["include", "exclude"] = "include"
    required_conditions: tuple[str, ...] = ()
    excluded_conditions: tuple[str, ...] = ()
    examples: tuple[str, ...] = ()


@dataclass(frozen=True)
class Match:
    detected: bool
    rule_id: str | None
    rule_title: str | None
    document_evidence: str | None
    transcript_evidence: str
    timestamp: float
    reason: str
    start: float
    end: float
    confidence: float | None = None


@dataclass
class VodInfo:
    url: str
    title: str
    streamer: str
    upload_date: str
    duration: float
    resolution: str | None = None
    media_path: str | None = None


def jsonable(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return {key: jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(item) for item in value]
    return value
