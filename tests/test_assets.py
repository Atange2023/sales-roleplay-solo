from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "assets" / "audio-manifest.json"
REQUIRED_FIELDS = {
    "id", "variant", "role", "scenario", "display_text", "spoken_text",
    "file", "fixed", "source", "generation",
}


class AssetManifestTests(unittest.TestCase):
    def test_manifest_indexes_all_145_legacy_mp3_files(self) -> None:
        self.assertTrue(MANIFEST.is_file(), "audio manifest is missing")
        entries = json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"]
        legacy = [item for item in entries if item["source"] == "v0.3-pre-generated"]
        packaged = [
            path
            for folder in ("audio", "audio3", "audio4")
            for path in (ROOT / folder).glob("*.mp3")
        ]
        self.assertEqual(len(packaged), 145)
        self.assertEqual(len(legacy), 145)
        self.assertEqual({item["file"] for item in legacy}, {p.relative_to(ROOT).as_posix() for p in packaged})

    def test_manifest_entries_are_complete_and_point_to_nonempty_files(self) -> None:
        self.assertTrue(MANIFEST.is_file(), "audio manifest is missing")
        entries = json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"]
        self.assertGreaterEqual(len(entries), 157)
        for item in entries:
            self.assertTrue(REQUIRED_FIELDS.issubset(item), item)
            self.assertTrue(item["display_text"])
            self.assertTrue(item["spoken_text"])
            path = ROOT / item["file"]
            self.assertTrue(path.is_file(), item["file"])
            self.assertGreater(path.stat().st_size, 1000, item["file"])

    def test_fixed_v04_system_and_role_endings_are_packaged(self) -> None:
        self.assertTrue(MANIFEST.is_file(), "audio manifest is missing")
        entries = json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"]
        ids = {item["id"] for item in entries if item["source"] == "v0.4-windows-sapi-pre-generated"}
        self.assertTrue(
            {"SYS_BOOT", "SYS_STAGE_CLEAR", "SYS_PROFESSIONAL_EXIT", "SYS_GAME_OVER", "SYS_ACHIEVEMENT"}.issubset(ids)
        )
        role_exits = [item for item in entries if item["id"] == "ROLE_PROFESSIONAL_EXIT"]
        self.assertEqual({item["role"] for item in role_exits}, {"zhang", "laozhao", "laowang", "zhous", "lin", "chen", "coach"})


if __name__ == "__main__":
    unittest.main()