from __future__ import annotations

import importlib.util
import unittest
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROGRESS_PATH = ROOT / "scripts" / "progress.py"
TMP_ROOT = ROOT / "tests" / ".tmp" / "progress-v043-direct"
TMP_ROOT.mkdir(parents=True, exist_ok=True)


def load_progress_module():
    spec = importlib.util.spec_from_file_location("progress_v043", PROGRESS_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class StageSpecificProgressTests(unittest.TestCase):
    def setUp(self) -> None:
        self.path = TMP_ROOT / f"{uuid.uuid4().hex}.json"

    def tearDown(self) -> None:
        self.path.unlink(missing_ok=True)

    def test_dlc02_professional_close_does_not_unlock_second_stage(self) -> None:
        progress = load_progress_module()
        progress.record_outcome(self.path, "DLC02", "L01", "professional_exit")
        status = progress.stage_status(progress.load_config(), progress.load_progress(self.path), "DLC02", "L02")
        self.assertEqual(status, "locked")

    def test_dlc02_stage_clear_unlocks_second_stage(self) -> None:
        progress = load_progress_module()
        progress.record_outcome(self.path, "DLC02", "L01", "stage_clear")
        status = progress.stage_status(progress.load_config(), progress.load_progress(self.path), "DLC02", "L02")
        self.assertEqual(status, "unlocked")


if __name__ == "__main__":
    unittest.main()
