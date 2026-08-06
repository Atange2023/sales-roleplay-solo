# -*- coding: utf-8 -*-
"""Generate the five deterministic v0.4 Standard MIDI File cues."""

from __future__ import annotations

import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "midi"
CUES = {
    "boot": [48, 55, 60, 67],
    "stage-clear": [60, 64, 67, 72],
    "professional-exit": [60, 62, 59, 55],
    "game-over": [55, 51, 48, 43],
    "achievement": [60, 64, 67, 72, 76, 79],
}


def variable_length(value: int) -> bytes:
    buffer = value & 0x7F
    result = bytearray([buffer])
    while value >> 7:
        value >>= 7
        buffer = (value & 0x7F) | 0x80
        result.insert(0, buffer)
    return bytes(result)


def build_midi(path: Path, notes: list[int], tempo: int = 500_000) -> Path:
    track = bytearray(b"\x00\xff\x51\x03" + tempo.to_bytes(3, "big"))
    track.extend(b"\x00\xc0\x50")
    for note in notes:
        track.extend(b"\x00\x90" + bytes([note, 88]))
        track.extend(variable_length(96) + b"\x80" + bytes([note, 0]))
    track.extend(b"\x00\xff\x2f\x00")
    header = b"MThd" + struct.pack(">IHHH", 6, 0, 1, 96)
    payload = header + b"MTrk" + struct.pack(">I", len(track)) + bytes(track)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return path


def main() -> int:
    for name, notes in CUES.items():
        build_midi(OUTPUT / f"{name}.mid", notes)
    print(f"generated {len(CUES)} MIDI cues in {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())