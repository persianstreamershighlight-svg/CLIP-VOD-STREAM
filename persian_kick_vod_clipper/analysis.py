from __future__ import annotations

from .models import Match, Rule, Segment


def match_transcript(segments: list[Segment], rules: list[Rule]) -> tuple[list[Match], list[Match]]:
    """Conservative literal matcher: no unstated synonyms, sentiment, or inferred criteria."""
    accepted, rejected = [], []
    exclusions = [r for r in rules if r.decision == "exclude"]
    for segment in segments:
        text = segment.text.casefold()
        blockers = [r for r in exclusions if r.definition.casefold() in text]
        for rule in (r for r in rules if r.decision == "include"):
            if rule.definition.casefold() not in text:
                continue
            blocked = blockers[0] if blockers else None
            detected = blocked is None
            result = Match(detected, rule.id, rule.title, rule.document_evidence, segment.text,
                           segment.start, ("مطابقت لفظی مستقیم با قانون سند" if detected else
                           f"رد بر اساس قانون حذف {blocked.id}"), segment.start, segment.end)
            (accepted if detected else rejected).append(result)
    return accepted, rejected

