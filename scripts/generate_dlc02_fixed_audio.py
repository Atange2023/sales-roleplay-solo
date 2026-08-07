# -*- coding: utf-8 -*-
"""Rebuild the distributable DLC02-L02 fixed MP3 assets with local Windows SAPI."""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "assets" / "fixed-lines.json"


def _escape_powershell(value: str) -> str:
    return value.replace("'", "''")


def synthesize(entry: dict) -> Path:
    destination = ROOT / entry["file"]
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="sales-roleplay-audio-") as temporary:
        wav = Path(temporary) / "line.wav"
        script = (
            "Add-Type -AssemblyName System.Speech; "
            "$s=New-Object System.Speech.Synthesis.SpeechSynthesizer; "
            f"$s.SetOutputToWaveFile('{_escape_powershell(str(wav))}'); "
            f"$s.Speak('{_escape_powershell(entry['spoken_text'])}'); "
            "$s.Dispose()"
        )
        subprocess.run(["powershell", "-NoProfile", "-Command", script], check=True, capture_output=True, text=True, encoding="utf-8")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-codec:a", "libmp3lame", "-q:a", "4", str(destination)], check=True)
    if not destination.is_file() or destination.stat().st_size <= 1_000:
        raise RuntimeError(f"audio generation failed: {destination}")
    return destination


def main() -> int:
    entries = json.loads(CATALOG.read_text(encoding="utf-8"))["entries"]
    targets = [item for item in entries if item["source"] == "v0.4.3-windows-sapi-pre-generated"]
    for item in targets:
        print(synthesize(item))
    print(f"GENERATED {len(targets)} DLC02 fixed MP3 files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
