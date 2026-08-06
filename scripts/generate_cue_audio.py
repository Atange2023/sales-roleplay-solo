# -*- coding: utf-8 -*-
"""Pre-render the MIDI melodies as portable retro WAV cue assets."""

from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

from generate_midi import CUES

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "cues"
RATE = 44_100
NOTE_SECONDS = 0.42
GAP_SECONDS = 0.04


def frequency(note: int) -> float:
    return 440.0 * (2.0 ** ((note - 69) / 12.0))


def build_wav(path: Path, notes: list[int]) -> Path:
    samples: list[int] = []
    note_frames = int(RATE * NOTE_SECONDS)
    gap_frames = int(RATE * GAP_SECONDS)
    for note in notes:
        hz = frequency(note)
        for frame in range(note_frames):
            t = frame / RATE
            attack = min(1.0, frame / (RATE * 0.02))
            release = min(1.0, (note_frames - frame) / (RATE * 0.10))
            envelope = attack * release
            lead = math.sin(2 * math.pi * hz * t) + 0.24 * math.sin(4 * math.pi * hz * t)
            bass = 0.30 * math.sin(2 * math.pi * (hz / 2) * t)
            samples.append(int(10_500 * envelope * (lead + bass) / 1.54))
        samples.extend([0] * gap_frames)
    samples.extend([0] * int(RATE * 0.20))
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(RATE)
        output.writeframes(b"".join(struct.pack("<h", max(-32768, min(32767, value))) for value in samples))
    return path


def main() -> int:
    for name, notes in CUES.items():
        build_wav(OUTPUT / f"{name}.wav", notes)
    print(f"generated {len(CUES)} rendered cue files in {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
