from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "tts_speak.py"


class AudioLookupTests(unittest.TestCase):
    def test_business_school_id_resolves_to_packaged_audio_offline(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--play",
                "B1_why_zhous",
                "--offline",
                "--no-launch",
            ],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            capture_output=True,
            timeout=10,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("audio4/zhous_B1_why_zhous_1.mp3", completed.stdout.replace("\\", "/"))
        self.assertNotIn("???", completed.stdout)


if __name__ == "__main__":
    unittest.main()
