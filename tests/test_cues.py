from __future__ import annotations

import json
import subprocess
import sys
import unittest
import wave
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAYER = ROOT / "scripts" / "media_player.py"
REQUIRED = ("boot", "stage-clear", "professional-exit", "game-over", "achievement")


class CueTests(unittest.TestCase):
    def test_all_five_midi_and_rendered_cues_are_valid_and_audible_length(self) -> None:
        for cue in REQUIRED:
            midi = ROOT / "assets" / "midi" / f"{cue}.mid"
            rendered = ROOT / "assets" / "cues" / f"{cue}.wav"
            self.assertTrue(midi.is_file(), cue)
            self.assertEqual(midi.read_bytes()[:4], b"MThd", cue)
            self.assertTrue(rendered.is_file(), cue)
            with wave.open(str(rendered), "rb") as source:
                self.assertGreater(source.getnframes() / source.getframerate(), 1.0, cue)

    def test_cue_dry_run_uses_packaged_rendered_audio(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(PLAYER), "cue", "boot", "--dry-run"],
            cwd=ROOT, text=True, encoding="utf-8", capture_output=True, timeout=10,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["backend"], "ffplay")
        self.assertEqual(Path(payload["path"]), ROOT / "assets" / "cues" / "boot.wav")

    def test_unknown_cue_returns_nonzero(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(PLAYER), "cue", "missing", "--dry-run"],
            cwd=ROOT, text=True, encoding="utf-8", capture_output=True, timeout=10,
        )
        self.assertEqual(completed.returncode, 2)
        self.assertIn("unknown cue", completed.stdout.lower())


if __name__ == "__main__":
    unittest.main()
