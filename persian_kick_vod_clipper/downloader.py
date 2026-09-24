from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yt_dlp

from .models import VodInfo


def validate_kick_url(url: str) -> str:
    if not re.fullmatch(r"https?://(?:www\.)?kick\.com/[A-Za-z0-9_-]+/videos/[A-Za-z0-9-]+/?", url):
        raise ValueError("نشانی باید لینک VOD در دامنه kick.com باشد")
    return url


class KickDownloader:
    def __init__(self, temp_dir: Path, cookie_file: Path | None = None):
        self.temp_dir, self.cookie_file = temp_dir, cookie_file

    def _options(self, download: bool) -> dict[str, Any]:
        options: dict[str, Any] = {"quiet": True, "noplaylist": True, "outtmpl": str(self.temp_dir / "vod.%(ext)s")}
        if self.cookie_file:
            options["cookiefile"] = str(self.cookie_file)
        if not download:
            options["skip_download"] = True
        return options

    def fetch(self, url: str) -> VodInfo:
        validate_kick_url(url)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        with yt_dlp.YoutubeDL(self._options(True)) as ydl:
            info = ydl.extract_info(url, download=True)
            path = ydl.prepare_filename(info)
        return VodInfo(url=url, title=info.get("title") or "", streamer=info.get("uploader") or "",
                       upload_date=info.get("upload_date") or "unknown", duration=float(info.get("duration") or 0),
                       resolution=info.get("resolution"), media_path=path)

