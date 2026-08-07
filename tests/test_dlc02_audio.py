from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "assets" / "audio-manifest.json"


class Dlc02FixedAudioTests(unittest.TestCase):
    def test_l02_openings_and_stable_endings_are_packaged_audio(self) -> None:
        entries = json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"]
        packaged = [item for item in entries if item["source"] == "v0.4.3-windows-sapi-pre-generated"]
        expected = {
            "L02_BOSS_OPEN", "L02_SCHOLAR_OPEN", "L02_EMPLOYEE_OPEN",
            "L02_CORPORATE_OPEN", "L02_RESOURCE_OPEN", "L02_NORMAL_PASS",
            "L02_SCHOLARSHIP_PASS", "L02_AID_PASS", "L02_SPECIAL_PASS",
            "L02_NONPASS", "L02_TIMEOUT", "L02_POLICY_FAILURE",
        }
        self.assertEqual({item["id"] for item in packaged}, expected)
        for item in packaged:
            path = ROOT / item["file"]
            self.assertTrue(path.is_file(), item["file"])
            self.assertGreater(path.stat().st_size, 1_000, item["file"])
            self.assertTrue(item["fixed"])


if __name__ == "__main__":
    unittest.main()
