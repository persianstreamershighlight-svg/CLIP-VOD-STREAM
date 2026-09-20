from __future__ import annotations

import hashlib
import logging
import time
from pathlib import Path

from .analysis import match_transcript
from .clipping import write_clip_bundle
from .config import Settings
from .document_rules import parse_explicit_rules, validate_criteria
from .downloader import KickDownloader
from .models import jsonable
from .reporting import write_report
from .state import ProcessingState
from .storage import GoogleDriveUploader
from .transcription import WhisperTranscriber, extract_audio, write_transcripts

log = logging.getLogger(__name__)


def run_pipeline(vod_url: str, streamer: str, criteria: str, settings: Settings,
                 glossary: str = "", upload: bool = False, reencode: bool = False) -> dict:
    started = time.monotonic()
    settings.prepare()
    criteria = validate_criteria(criteria)  # fail closed before downloading anything
    rules = parse_explicit_rules(criteria)
    job_id = hashlib.sha256(vod_url.encode()).hexdigest()[:16]
    job = settings.output_dir / job_id
    state = ProcessingState(job / "state.json")
    if state.done("finished"):
        raise RuntimeError("این VOD قبلاً به طور کامل پردازش شده است")

    vod = KickDownloader(settings.temp_dir / job_id, settings.kick_cookie_file).fetch(vod_url)
    vod.streamer = streamer or vod.streamer
    state.complete("download")
    audio = settings.temp_dir / job_id / "audio.wav"
    extract_audio(Path(vod.media_path or ""), audio)
    state.complete("audio")
    segments = WhisperTranscriber(settings.whisper_model).transcribe(audio, glossary)
    write_transcripts(segments, job / "transcripts")
    state.complete("transcription")
    accepted, rejected = match_transcript(segments, rules)
    clips = [write_clip_bundle(job, Path(vod.media_path or ""), vod, item, reencode) for item in accepted]
    state.complete("clipping")

    links: dict[str, str] = {}
    if upload:
        if not settings.google_service_account_file or not settings.google_drive_folder_id:
            raise RuntimeError("اطلاعات امن Google Drive تنظیم نشده است")
        uploader = GoogleDriveUploader(settings.google_service_account_file, settings.google_drive_folder_id)
        for path in clips:
            links[path.name] = uploader.upload(path)
        state.complete("upload")
    report = {"vod_url": vod.url, "vod_title": vod.title, "streamer": vod.streamer,
              "processing_seconds": round(time.monotonic() - started, 3), "segments_checked": len(segments),
              "moments_detected": len(accepted), "clips_created": len(clips), "clips_uploaded": len(links),
              "drive_links": links, "accepted": jsonable(accepted), "rejected": jsonable(rejected),
              "errors": [], "warnings": []}
    write_report(job / "reports", report)
    state.complete("finished")
    log.info("پردازش کامل شد: %s", job_id)
    return report

