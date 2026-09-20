from __future__ import annotations

import json
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from .models import Match, VodInfo


def clip_bounds(timestamp: float, duration: float, before: float = 180, after: float = 180) -> tuple[float, float]:
    return max(0.0, timestamp - before), min(duration, timestamp + after)


def create_clip(video: Path, destination: Path, start: float, end: float, reencode: bool = False) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    codec = ["-c:v", "libx264", "-c:a", "aac"] if reencode else ["-c", "copy"]
    subprocess.run(["ffmpeg", "-y", "-ss", str(start), "-i", str(video), "-t", str(end-start), *codec, str(destination)], check=True)


def write_clip_bundle(base: Path, video: Path, vod: VodInfo, match: Match, reencode: bool = False) -> Path:
    start, end = clip_bounds(match.timestamp, vod.duration)
    safe = re.sub(r"[^\w.-]+", "_", vod.streamer, flags=re.UNICODE)
    stem = f"{safe}_{vod.upload_date}_{match.timestamp:.1f}_{match.rule_id}"
    clip = base / "clips" / f"{stem}.mp4"
    create_clip(video, clip, start, end, reencode)
    metadata = {"streamer": vod.streamer, "vod_url": vod.url, "vod_title": vod.title,
                "clip_start": start, "clip_end": end, "detected_timestamp": match.timestamp,
                "rule_id": match.rule_id, "rule_title": match.rule_title,
                "document_evidence": match.document_evidence, "transcript_evidence": match.transcript_evidence,
                "created_at": datetime.now(UTC).isoformat()}
    report = base / "reports"
    report.mkdir(parents=True, exist_ok=True)
    (report / f"{stem}.metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    (report / f"{stem}.reason.txt").write_text(match.reason, encoding="utf-8")
    (base / "transcripts").mkdir(parents=True, exist_ok=True)
    (base / "transcripts" / f"{stem}.txt").write_text(match.transcript_evidence, encoding="utf-8")
    return clip
