from __future__ import annotations

import json
import subprocess
from pathlib import Path

from .models import Segment, jsonable


def extract_audio(video: Path, audio: Path) -> None:
    subprocess.run(["ffmpeg", "-y", "-i", str(video), "-vn", "-ac", "1", "-ar", "16000", str(audio)], check=True)


class WhisperTranscriber:
    def __init__(self, model_name: str):
        from faster_whisper import WhisperModel
        self.model = WhisperModel(model_name)

    def transcribe(self, audio: Path, glossary: str = "") -> list[Segment]:
        segments, _ = self.model.transcribe(str(audio), language="fa", initial_prompt=glossary or None)
        return [Segment(float(s.start), float(s.end), s.text.strip()) for s in segments]


def write_transcripts(segments: list[Segment], directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "transcript.txt").write_text("\n".join(s.text for s in segments), encoding="utf-8")
    payload = {"language": "fa", "segments": jsonable(segments)}
    (directory / "transcript.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    blocks = []
    for i, s in enumerate(segments, 1):
        def stamp(t: float) -> str:
            ms = round(t * 1000)
            h, ms = divmod(ms, 3600000)
            m, ms = divmod(ms, 60000)
            sec, ms = divmod(ms, 1000)
            return f"{h:02}:{m:02}:{sec:02},{ms:03}"
        blocks.append(f"{i}\n{stamp(s.start)} --> {stamp(s.end)}\n{s.text}\n")
    (directory / "transcript.srt").write_text("\n".join(blocks), encoding="utf-8")
