from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UPDATER_PATH = ROOT / "scripts" / "update_skill.py"
TMP_ROOT = ROOT / "tests" / ".tmp" / "update"
TMP_ROOT.mkdir(parents=True, exist_ok=True)


def load_updater():
    if not UPDATER_PATH.is_file():
        raise AssertionError("scripts/update_skill.py is missing")
    spec = importlib.util.spec_from_file_location("update_skill", UPDATER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def build_release_zip(base: Path, version: str = "v0.4.1") -> tuple[Path, str]:
    archive = base / "sales-roleplay-solo-offline.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as handle:
        handle.writestr("sales-roleplay-solo/SKILL.md", f"release {version}\n")
        handle.writestr(
            "sales-roleplay-solo/assets/version.json",
            json.dumps({"version": version, "repository": "Atange2023/sales-roleplay-solo"}),
        )
        handle.writestr("sales-roleplay-solo/scripts/update_skill.py", "# packaged updater\n")
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    return archive, digest


class UpdateTests(unittest.TestCase):
    def test_apply_archive_preserves_user_data_and_creates_rollback_backup(self) -> None:
        updater = load_updater()
        with tempfile.TemporaryDirectory(dir=TMP_ROOT) as tmp:
            base = Path(tmp)
            install = base / "sales-roleplay-solo"
            (install / "data").mkdir(parents=True)
            (install / "reports").mkdir()
            (install / "assets").mkdir()
            (install / "SKILL.md").write_text("release v0.4.0\n", encoding="utf-8")
            (install / "assets" / "version.json").write_text(
                json.dumps({"version": "v0.4.0"}), encoding="utf-8"
            )
            (install / "data" / "sessions.jsonl").write_text("training-log\n", encoding="utf-8")
            (install / "reports" / "weekly-report.html").write_text("weekly-report\n", encoding="utf-8")
            archive, digest = build_release_zip(base)

            result = updater.apply_archive(archive, install, expected_sha256=digest)

            self.assertEqual(result["from_version"], "v0.4.0")
            self.assertEqual(result["to_version"], "v0.4.1")
            self.assertEqual((install / "SKILL.md").read_text(encoding="utf-8"), "release v0.4.1\n")
            self.assertEqual((install / "data" / "sessions.jsonl").read_text(encoding="utf-8"), "training-log\n")
            self.assertEqual(
                (install / "reports" / "weekly-report.html").read_text(encoding="utf-8"),
                "weekly-report\n",
            )
            backup = Path(result["backup"])
            self.assertTrue(backup.is_dir())
            self.assertEqual((backup / "SKILL.md").read_text(encoding="utf-8"), "release v0.4.0\n")

    def test_checksum_mismatch_aborts_before_installation_changes(self) -> None:
        updater = load_updater()
        with tempfile.TemporaryDirectory(dir=TMP_ROOT) as tmp:
            base = Path(tmp)
            install = base / "sales-roleplay-solo"
            install.mkdir()
            skill = install / "SKILL.md"
            skill.write_text("release v0.4.0\n", encoding="utf-8")
            archive, _ = build_release_zip(base)

            with self.assertRaises(updater.UpdateError):
                updater.apply_archive(archive, install, expected_sha256="0" * 64)

            self.assertEqual(skill.read_text(encoding="utf-8"), "release v0.4.0\n")

    def test_rollback_restores_previous_code_but_keeps_new_training_data(self) -> None:
        updater = load_updater()
        with tempfile.TemporaryDirectory(dir=TMP_ROOT) as tmp:
            base = Path(tmp)
            install = base / "sales-roleplay-solo"
            (install / "data").mkdir(parents=True)
            (install / "assets").mkdir()
            (install / "SKILL.md").write_text("release v0.4.0\n", encoding="utf-8")
            (install / "assets" / "version.json").write_text(
                json.dumps({"version": "v0.4.0"}), encoding="utf-8"
            )
            (install / "data" / "sessions.jsonl").write_text("before\n", encoding="utf-8")
            archive, digest = build_release_zip(base)
            updater.apply_archive(archive, install, expected_sha256=digest)
            (install / "data" / "sessions.jsonl").write_text("before\nafter\n", encoding="utf-8")

            result = updater.rollback_latest(install)

            self.assertEqual(result["restored_version"], "v0.4.0")
            self.assertEqual((install / "SKILL.md").read_text(encoding="utf-8"), "release v0.4.0\n")
            self.assertEqual((install / "data" / "sessions.jsonl").read_text(encoding="utf-8"), "before\nafter\n")

    def test_release_asset_selection_requires_zip_and_sha256_manifest(self) -> None:
        updater = load_updater()
        payload = {
            "tag_name": "v0.4.1",
            "assets": [
                {"name": "sales-roleplay-solo-v0.4.1-offline.zip", "browser_download_url": "https://example/skill.zip"},
                {"name": "SHA256SUMS.txt", "browser_download_url": "https://example/SHA256SUMS.txt"},
            ],
        }

        selected = updater.select_release_assets(payload)

        self.assertEqual(selected["version"], "v0.4.1")
        self.assertEqual(selected["zip_name"], "sales-roleplay-solo-v0.4.1-offline.zip")
        self.assertEqual(selected["sha_url"], "https://example/SHA256SUMS.txt")


if __name__ == "__main__":
    unittest.main()
