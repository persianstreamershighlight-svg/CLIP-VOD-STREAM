import json

import pytest

from persian_kick_vod_clipper.analysis import match_transcript
from persian_kick_vod_clipper.clipping import clip_bounds
from persian_kick_vod_clipper.document_rules import CriteriaError, parse_explicit_rules, validate_criteria
from persian_kick_vod_clipper.downloader import validate_kick_url
from persian_kick_vod_clipper.models import Segment
from persian_kick_vod_clipper.transcription import write_transcripts


def test_empty_criteria_fails_closed():
    with pytest.raises(CriteriaError):
        validate_criteria(" \n ")


def test_parser_preserves_exact_evidence():
    rules = parse_explicit_rules("عبارت خوب\nمنع: اسپویل")
    assert rules[0].document_evidence == "عبارت خوب"
    assert rules[1].definition == "اسپویل"
    assert rules[1].decision == "exclude"


def test_matcher_only_uses_literal_document_rule():
    rules = parse_explicit_rules("بردیم\nمنع: اسپویل")
    accepted, rejected = match_transcript([
        Segment(10, 12, "بالاخره بردیم"), Segment(20, 22, "چه هیجان انگیز"),
        Segment(30, 32, "بردیم ولی اسپویل")], rules)
    assert [m.timestamp for m in accepted] == [10]
    assert len(rejected) == 1


def test_clip_bounds_are_clamped():
    assert clip_bounds(100, 1000) == (0, 280)
    assert clip_bounds(950, 1000) == (770, 1000)


def test_url_validation():
    assert validate_kick_url("https://kick.com/name/videos/abc-123")
    with pytest.raises(ValueError):
        validate_kick_url("https://example.com/video")


def test_transcript_outputs(tmp_path):
    write_transcripts([Segment(1.2, 2.3, "سلام")], tmp_path)
    assert json.loads((tmp_path / "transcript.json").read_text())["language"] == "fa"
    assert "00:00:01,200 --> 00:00:02,300" in (tmp_path / "transcript.srt").read_text()

