# -*- coding: utf-8 -*-
"""Real local media and game-cue playback with visible results."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CUE_DIR = ROOT / "assets" / "cues"
KNOWN_CUES = {"boot", "stage-clear", "professional-exit", "game-over", "achievement"}


@dataclass(frozen=True)
class PlaybackResult:
    ok: bool
    backend: str
    path: str
    error: str | None = None


def probe_file(path: Path | str) -> PlaybackResult:
    source = Path(path).resolve()
    if not source.is_file():
        return PlaybackResult(False, "none", str(source), "file does not exist")
    if source.stat().st_size <= 0:
        return PlaybackResult(False, "none", str(source), "file is empty")
    if source.suffix.lower() not in {".mp3", ".wav", ".mid", ".midi"}:
        return PlaybackResult(False, "none", str(source), "unsupported media type")
    return PlaybackResult(True, "probe", str(source))


def play_file(path: Path | str, *, wait: bool = True, dry_run: bool = False) -> PlaybackResult:
    checked = probe_file(path)
    if not checked.ok:
        return checked
    source = Path(checked.path)
    ffplay = shutil.which("ffplay")
    if not ffplay:
        return PlaybackResult(False, "none", str(source), "ffplay is not installed")
    result = PlaybackResult(True, "ffplay", str(source))
    if dry_run:
        return result
    command = [ffplay, "-nodisp", "-autoexit", "-loglevel", "error", str(source)]
    if wait:
        completed = subprocess.run(command, check=False)
        if completed.returncode != 0:
            return PlaybackResult(False, "ffplay", str(source), f"ffplay exited {completed.returncode}")
    else:
        subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return result


def play_cue(cue_id: str, *, wait: bool = True, dry_run: bool = False) -> PlaybackResult:
    if cue_id not in KNOWN_CUES:
        return PlaybackResult(False, "none", cue_id, "unknown cue")
    return play_file(CUE_DIR / f"{cue_id}.wav", wait=wait, dry_run=dry_run)


def _print(result: PlaybackResult) -> None:
    print(json.dumps(asdict(result), ensure_ascii=False))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    probe = subparsers.add_parser("probe")
    probe.add_argument("path", type=Path)
    play = subparsers.add_parser("play")
    play.add_argument("path", type=Path)
    play.add_argument("--dry-run", action="store_true")
    play.add_argument("--no-wait", action="store_true")
    cue = subparsers.add_parser("cue")
    cue.add_argument("cue_id")
    cue.add_argument("--dry-run", action="store_true")
    cue.add_argument("--no-wait", action="store_true")
    args = parser.parse_args(argv)
    if args.command == "probe":
        result = probe_file(args.path)
    elif args.command == "play":
        result = play_file(args.path, wait=not args.no_wait, dry_run=args.dry_run)
    else:
        result = play_cue(args.cue_id, wait=not args.no_wait, dry_run=args.dry_run)
    _print(result)
    return 0 if result.ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
