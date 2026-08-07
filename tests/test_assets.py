from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "assets" / "audio-manifest.json"
REQUIRED_FIELDS = {"id", "variant", "role", "role_name", "scenario", "display_text", "spoken_text", "file", "fixed", "source", "generation"}


class AssetManifestTests(unittest.TestCase):
    def test_manifest_indexes_all_145_legacy_mp3_files(self) -> None:
        entries = json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"]
        legacy = [item for item in entries if item["source"] == "v0.3-pre-generated"]
        packaged = [path for folder in ("audio", "audio3", "audio4") for path in (ROOT / folder).glob("*.mp3")]
        self.assertEqual(len(packaged), 145)
        self.assertEqual(len(legacy), 145)
        self.assertEqual({item["file"] for item in legacy}, {path.relative_to(ROOT).as_posix() for path in packaged})

    def test_manifest_has_exactly_181_complete_nonempty_entries(self) -> None:
        entries = json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"]
        self.assertEqual(len(entries), 181)
        for item in entries:
            self.assertTrue(REQUIRED_FIELDS.issubset(item), item)
            self.assertTrue(item["display_text"])
            self.assertTrue(item["spoken_text"])
            path = ROOT / item["file"]
            self.assertTrue(path.is_file(), item["file"])
            self.assertGreater(path.stat().st_size, 1_000, item["file"])

    def test_fixed_system_and_role_endings_are_packaged(self) -> None:
        entries = json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"]
        fixed = [item for item in entries if item["source"] == "v0.4-windows-sapi-pre-generated"]
        self.assertEqual(len(fixed), 24)
        ids = {item["id"] for item in fixed}
        self.assertTrue({"SYS_BOOT", "SYS_STAGE_CLEAR", "SYS_PROFESSIONAL_EXIT", "SYS_GAME_OVER", "SYS_ACHIEVEMENT"}.issubset(ids))
        exits = [item for item in fixed if item["id"] == "ROLE_PROFESSIONAL_EXIT"]
        self.assertEqual({item["role"] for item in exits}, {"zhang", "laozhao", "laowang", "zhous", "lin", "chen", "coach"})


if __name__ == "__main__":
    unittest.main()
