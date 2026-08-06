from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MIDI_DIR = ROOT / "assets" / "midi"
CUES = ("boot", "stage-clear", "professional-exit", "game-over", "achievement")


class MidiAssetTests(unittest.TestCase):
    def test_all_required_midi_cues_are_valid_format_zero_files(self) -> None:
        for cue in CUES:
            path = MIDI_DIR / f"{cue}.mid"
            self.assertTrue(path.is_file(), f"missing {cue}")
            data = path.read_bytes()
            self.assertGreater(len(data), 30)
            self.assertEqual(data[:4], b"MThd")
            self.assertEqual(int.from_bytes(data[8:10], "big"), 0)
            self.assertIn(b"MTrk", data)


if __name__ == "__main__":
    unittest.main()