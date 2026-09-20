from __future__ import annotations

import io
import re
from pathlib import Path

import requests
from docx import Document

from .models import Rule


class CriteriaError(ValueError):
    pass


def read_docx(data: bytes) -> str:
    try:
        text = "\n".join(p.text for p in Document(io.BytesIO(data)).paragraphs).strip()
    except Exception as exc:
        raise CriteriaError(f"فایل DOCX قابل استخراج نیست: {exc}") from exc
    return validate_criteria(text)


def read_text_file(path: Path) -> str:
    if path.suffix.lower() == ".docx":
        return read_docx(path.read_bytes())
    return validate_criteria(path.read_text(encoding="utf-8"))


def read_google_doc(url_or_id: str, timeout: int = 30) -> str:
    match = re.search(r"/document/d/([\w-]+)", url_or_id)
    document_id = match.group(1) if match else url_or_id.strip()
    if not re.fullmatch(r"[\w-]{10,}", document_id):
        raise CriteriaError("شناسه یا نشانی Google Doc معتبر نیست")
    url = f"https://docs.google.com/document/d/{document_id}/export?format=txt"
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise CriteriaError(f"Google Doc قابل خواندن نیست: {exc}") from exc
    return validate_criteria(response.text)


def validate_criteria(text: str) -> str:
    normalized = text.replace("\ufeff", "").strip()
    if not normalized:
        raise CriteriaError("معیارها خالی یا غیرقابل استخراج‌اند؛ پردازش متوقف شد")
    return normalized


def parse_explicit_rules(text: str) -> list[Rule]:
    """Parse lines without inventing semantics. Prefix `منع:` creates an exclusion."""
    text = validate_criteria(text)
    lines = [line.strip(" \t-•") for line in text.splitlines() if line.strip(" \t-•")]
    rules: list[Rule] = []
    for index, line in enumerate(lines, 1):
        excluded = line.startswith(("منع:", "حذف:", "EXCLUDE:"))
        definition = line.split(":", 1)[1].strip() if excluded and ":" in line else line
        if not definition:
            continue
        rules.append(Rule(id=f"rule_{index:03d}", title=line[:80], definition=definition,
                          document_evidence=line, decision="exclude" if excluded else "include"))
    if not rules:
        raise CriteriaError("هیچ قانون صریحی از معیارها استخراج نشد")
    return rules

