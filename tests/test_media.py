from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TTS = ROOT / "scripts" / "tts_speak.py"
PLAYER = ROOT / "scripts" / "media_player.py"
SAMPLE = ROOT / "audio4" / "zhous_B0_open_zhous_1.mp3"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=10,
    )


class MediaTests(unittest.TestCase):
    def test_business_school_id_resolves_to_existing_local_audio_offline(self) -> None:
        completed = run(str(TTS), "--play", "B1_why_zhous", "--offline", "--no-launch")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("LOCAL -> audio4/zhous_B1_why_zhous_1.mp3", completed.stdout)

    def test_unknown_line_id_returns_nonzero(self) -> None:
        completed = run(str(TTS), "--play", "DOES_NOT_EXIST", "--offline", "--no-launch")
        self.assertEqual(completed.returncode, 2)
        self.assertIn("unknown line id", completed.stderr.lower())

    def test_probe_accepts_real_mp3_and_rejects_missing_file(self) -> None:
        valid = run(str(PLAYER), "probe", str(SAMPLE))
        missing = run(str(PLAYER), "probe", str(ROOT / "audio" / "missing.mp3"))
        self.assertEqual(valid.returncode, 0, valid.stderr)
        self.assertIn('"ok": true', valid.stdout.lower())
        self.assertEqual(missing.returncode, 2)
        self.assertIn('"ok": false', missing.stdout.lower())

    def test_mp3_dry_run_selects_real_ffplay_backend(self) -> None:
        completed = run(str(PLAYER), "play", str(SAMPLE), "--dry-run")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn('"backend": "ffplay"', completed.stdout.lower())


if __name__ == "__main__":
    unittest.main()
