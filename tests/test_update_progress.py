from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class UpdateProgressTests(unittest.TestCase):
    def test_portable_update_preserves_progress(self) -> None:
        updater_path = ROOT / "scripts" / "update_skill.py"
        self.assertTrue(updater_path.is_file(), "updater is missing")
        spec = importlib.util.spec_from_file_location("update_skill_progress", updater_path)
        updater = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(updater)
        tmp_root = ROOT / "tests" / ".tmp" / "update-progress"
        tmp_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=tmp_root) as temporary:
            base = Path(temporary)
            install = base / "sales-roleplay-solo"
            (install / "assets").mkdir(parents=True)
            (install / "data").mkdir()
            (install / "SKILL.md").write_text("release v0.4.1\n", encoding="utf-8")
            (install / "assets" / "version.json").write_text(json.dumps({"version": "v0.4.1"}), encoding="utf-8")
            progress = '{"schema_version":"1.0","dlcs":{"DLC01":{"completed":["L01"]}}}\n'
            (install / "data" / "progress.json").write_text(progress, encoding="utf-8")
            archive = base / "release.zip"
            with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as handle:
                handle.writestr("sales-roleplay-solo/SKILL.md", "release v0.4.2\n")
                handle.writestr("sales-roleplay-solo/assets/version.json", json.dumps({"version": "v0.4.2"}))
                handle.writestr("sales-roleplay-solo/scripts/update_skill.py", "# packaged updater\n")
            digest = hashlib.sha256(archive.read_bytes()).hexdigest()

            updater.apply_archive(archive, install, expected_sha256=digest)

            self.assertEqual((install / "data" / "progress.json").read_text(encoding="utf-8"), progress)


if __name__ == "__main__":
    unittest.main()
