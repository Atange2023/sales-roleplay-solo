# -*- coding: utf-8 -*-
"""Offline-first fixed-line audio lookup with compatible v0.3 batch commands."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import tempfile
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from build_audio_manifest import scenario_entries
from media_player import play_file

MANIFEST = ROOT / "assets" / "audio-manifest.json"
DEFAULT_VOICE = "zh-CN-YunyangNeural"
DEFAULT_RATE = "-8%"


def load_catalog() -> list[dict]:
    if MANIFEST.is_file():
        return json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"]
    return scenario_entries()


def resolve_line(line_id: str, variant: int = 1) -> dict | None:
    for entry in load_catalog():
        if entry["id"] == line_id and int(entry.get("variant", 1)) == variant:
            return entry
    return None


def speak_dynamic(text: str, voice: str = DEFAULT_VOICE, rate: str = DEFAULT_RATE, *, launch: bool = True, output: Path | None = None, retries: int = 3) -> Path:
    import edge_tts

    destination = output or Path(tempfile.gettempdir()) / f"sales-roleplay-{os.getpid()}.mp3"

    async def generate() -> None:
        await edge_tts.Communicate(text, voice, rate=rate).save(str(destination))

    for attempt in range(1, retries + 1):
        try:
            asyncio.run(generate())
            break
        except Exception:
            if attempt == retries:
                raise
            time.sleep(attempt)
    if launch:
        result = play_file(destination)
        if not result.ok:
            raise RuntimeError(result.error)
    return destination


def speak(text, voice=DEFAULT_VOICE, rate=DEFAULT_RATE, play=True, out=None, quiet=False, retries=3):
    """v0.3-compatible dynamic TTS entry point."""
    path = speak_dynamic(text, voice, rate, launch=play, output=Path(out) if out else None, retries=retries)
    if not quiet:
        print("OK ->", path)
    return str(path)


def _batch(database: Path, audio_dir: Path, multi_role: bool) -> int:
    data = json.loads(database.read_text(encoding="utf-8"))
    items = data["branches"] if multi_role else data["openings"] + data["branches"]
    audio_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for item in items:
        texts = item.get("replies") or [item["text"]]
        if multi_role:
            role = item["char"]
            actor = data["characters"][role]
            prefix = f"{role}_"
        else:
            actor = data["persona"]
            prefix = ""
        for variant, text in enumerate(texts, 1):
            speak(text, voice=actor["voice"], rate=actor["rate"], play=False,
                  out=audio_dir / f"{prefix}{item['id']}_{variant}.mp3", quiet=True)
            count += 1
    return count


def play_by_id(line_id: str, *, variant: int = 1, launch: bool = True, offline: bool = False):
    entry = resolve_line(line_id, variant)
    if entry is None:
        return None
    local = ROOT / entry["file"]
    if local.is_file() and local.stat().st_size > 0:
        if launch:
            result = play_file(local)
            if not result.ok:
                return ("error", result.error or "playback failed")
        return ("local", entry["file"])
    if offline:
        return ("text", entry["display_text"])
    generation = entry.get("generation", {})
    path = speak_dynamic(entry["spoken_text"], generation.get("voice", DEFAULT_VOICE),
                         generation.get("rate", DEFAULT_RATE), launch=launch)
    return ("dynamic", str(path))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--play", metavar="ID")
    parser.add_argument("--variant", type=int, default=1)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--no-launch", action="store_true")
    parser.add_argument("--batch", action="store_true")
    parser.add_argument("--batch3", action="store_true")
    parser.add_argument("--batch4", action="store_true")
    parser.add_argument("--voice", default=DEFAULT_VOICE)
    parser.add_argument("--rate", default=DEFAULT_RATE)
    parser.add_argument("text", nargs="?")
    args = parser.parse_args(argv)
    if args.batch or args.batch3 or args.batch4:
        if args.batch:
            count = _batch(ROOT / "scenarios" / "zhang_dialogue.json", ROOT / "audio", False)
        elif args.batch3:
            count = _batch(ROOT / "scenarios" / "three_party_dialogue.json", ROOT / "audio3", True)
        else:
            count = _batch(ROOT / "scenarios" / "business_school_dialogue.json", ROOT / "audio4", True)
        print(f"BATCH -> {count}")
        return 0
    if args.play:
        result = play_by_id(args.play, variant=args.variant, launch=not args.no_launch, offline=args.offline)
        if result is None:
            print(f"ERROR unknown line id: {args.play}", file=sys.stderr)
            return 2
        mode, value = result
        print(f"{mode.upper()} -> {value}")
        return 0 if mode != "error" else 2
    if args.text:
        if args.offline:
            print(f"TEXT -> {args.text}")
            return 0
        path = speak_dynamic(args.text, args.voice, args.rate, launch=not args.no_launch)
        print(f"DYNAMIC -> {path}")
        return 0
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
