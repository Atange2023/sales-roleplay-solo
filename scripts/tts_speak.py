# -*- coding: utf-8 -*-
"""Offline-first fixed-line audio lookup with optional dynamic TTS fallback."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "assets" / "audio-manifest.json"
DATABASES = (
    (ROOT / "scenarios" / "zhang_dialogue.json", ROOT / "audio", False),
    (ROOT / "scenarios" / "three_party_dialogue.json", ROOT / "audio3", True),
    (ROOT / "scenarios" / "business_school_dialogue.json", ROOT / "audio4", True),
)
DEFAULT_VOICE = "zh-CN-YunyangNeural"
DEFAULT_RATE = "-8%"


def _scenario_entries() -> list[dict]:
    entries: list[dict] = []
    for database, audio_dir, multi_role in DATABASES:
        data = json.loads(database.read_text(encoding="utf-8"))
        items = data["branches"] if multi_role else data["openings"] + data["branches"]
        for item in items:
            texts = item.get("replies") or [item["text"]]
            if multi_role:
                actor = data["characters"][item["char"]]
                role_id = item["char"]
                prefix = f"{role_id}_"
            else:
                actor = data["persona"]
                role_id = "zhang"
                prefix = ""
            for variant, spoken in enumerate(texts, 1):
                path = audio_dir / f"{prefix}{item['id']}_{variant}.mp3"
                entries.append(
                    {
                        "id": item["id"],
                        "variant": variant,
                        "role": role_id,
                        "role_name": actor.get("name", role_id),
                        "scenario": data.get("scene", "manufacturing-single"),
                        "display_text": spoken,
                        "spoken_text": spoken,
                        "file": path.relative_to(ROOT).as_posix(),
                        "fixed": True,
                        "source": "v0.3-pre-generated",
                        "generation": {
                            "voice": actor.get("voice", DEFAULT_VOICE),
                            "rate": actor.get("rate", DEFAULT_RATE),
                        },
                    }
                )
    return entries


def load_catalog() -> list[dict]:
    if MANIFEST.exists():
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        return data["entries"]
    return _scenario_entries()


def resolve_line(line_id: str, variant: int = 1) -> dict | None:
    for item in load_catalog():
        if item["id"] == line_id and int(item.get("variant", 1)) == variant:
            return item
    return None


def _launch(path: Path) -> None:
    subprocess.run(
        ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", str(path)],
        check=False,
    )


def speak_dynamic(
    text: str,
    voice: str = DEFAULT_VOICE,
    rate: str = DEFAULT_RATE,
    *,
    launch: bool = True,
    output: Path | None = None,
    retries: int = 3,
) -> Path:
    """Generate online fallback audio. Never used in offline mode."""
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
        _launch(destination)
    return destination


def play_by_id(
    line_id: str,
    *,
    variant: int = 1,
    launch: bool = True,
    offline: bool = False,
) -> tuple[str, str] | None:
    entry = resolve_line(line_id, variant)
    if entry is None:
        return None
    local = ROOT / entry["file"]
    if local.is_file() and local.stat().st_size > 0:
        if launch:
            _launch(local)
        return ("local", entry["file"])
    if offline:
        return ("text", entry["display_text"])
    generation = entry.get("generation", {})
    path = speak_dynamic(
        entry["spoken_text"],
        generation.get("voice", DEFAULT_VOICE),
        generation.get("rate", DEFAULT_RATE),
        launch=launch,
    )
    return ("dynamic", str(path))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--play", metavar="ID")
    parser.add_argument("--variant", type=int, default=1)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--no-launch", action="store_true")
    parser.add_argument("text", nargs="?")
    args = parser.parse_args(argv)

    if args.play:
        result = play_by_id(
            args.play,
            variant=args.variant,
            launch=not args.no_launch,
            offline=args.offline,
        )
        if result is None:
            print(f"ERROR unknown line id: {args.play}", file=sys.stderr)
            return 2
        mode, value = result
        print(f"{mode.upper()} -> {value}")
        return 0
    if args.text:
        if args.offline:
            print(f"TEXT -> {args.text}")
            return 0
        path = speak_dynamic(args.text, launch=not args.no_launch)
        print(f"DYNAMIC -> {path}")
        return 0
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())