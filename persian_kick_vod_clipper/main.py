from __future__ import annotations

import logging
from pathlib import Path
from typing import Annotated

import typer

from .config import Settings
from .document_rules import read_google_doc, read_text_file, validate_criteria
from .pipeline import run_pipeline

app = typer.Typer(help="Persian Kick VOD Clipper")


@app.command()
def run(vod_url: str, streamer: str,
        criteria_text: Annotated[str | None, typer.Option()] = None,
        criteria_file: Annotated[Path | None, typer.Option()] = None,
        google_doc: Annotated[str | None, typer.Option()] = None,
        glossary: str = "", upload: bool = False, reencode: bool = False) -> None:
    sources = sum(value is not None for value in (criteria_text, criteria_file, google_doc))
    if sources != 1:
        raise typer.BadParameter("دقیقاً یکی از criteria-text، criteria-file یا google-doc لازم است")
    settings = Settings()
    settings.prepare()
    logging.basicConfig(level=settings.log_level, filename=settings.output_dir / "processing.log",
                        format="%(asctime)s %(levelname)s %(name)s %(message)s")
    criteria = (validate_criteria(criteria_text) if criteria_text is not None else
                read_text_file(criteria_file) if criteria_file is not None else read_google_doc(google_doc or ""))
    report = run_pipeline(vod_url, streamer, criteria, settings, glossary, upload, reencode)
    typer.echo(f"{report['clips_created']} کلیپ ساخته شد")


if __name__ == "__main__":
    app()
