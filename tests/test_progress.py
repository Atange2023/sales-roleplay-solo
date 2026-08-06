from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROGRESS = ROOT / "scripts" / "progress.py"
TMP_ROOT = ROOT / "tests" / ".tmp" / "progress"
TMP_ROOT.mkdir(parents=True, exist_ok=True)


def run_progress(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(PROGRESS), *args], cwd=ROOT,
                          text=True, encoding="utf-8", capture_output=True, timeout=10)


class ProgressTests(unittest.TestCase):
    def test_stage_clear_and_professional_exit_unlock_next_stage(self) -> None:
        for outcome in ("stage_clear", "professional_exit"):
            with self.subTest(outcome=outcome), tempfile.TemporaryDirectory(dir=TMP_ROOT) as tmp:
                path = Path(tmp) / "progress.json"
                recorded = run_progress("record", "--path", str(path), "--dlc", "DLC01", "--stage", "L01", "--outcome", outcome)
                status = run_progress("status", "--path", str(path), "--dlc", "DLC01", "--stage", "L02")
                self.assertEqual(recorded.returncode, 0, recorded.stderr)
                self.assertEqual(status.returncode, 0, status.stderr)
                self.assertEqual(status.stdout.strip(), "unlocked")

    def test_failure_outcomes_do_not_unlock_next_stage(self) -> None:
        for outcome in ("needs_practice", "game_over"):
            with self.subTest(outcome=outcome), tempfile.TemporaryDirectory(dir=TMP_ROOT) as tmp:
                path = Path(tmp) / "progress.json"
                run_progress("record", "--path", str(path), "--dlc", "DLC01", "--stage", "L01", "--outcome", outcome)
                status = run_progress("status", "--path", str(path), "--dlc", "DLC01", "--stage", "L02")
                self.assertEqual(status.stdout.strip(), "locked")

    def test_each_dlc_first_stage_is_independently_unlocked(self) -> None:
        with tempfile.TemporaryDirectory(dir=TMP_ROOT) as tmp:
            path = Path(tmp) / "progress.json"
            first = run_progress("status", "--path", str(path), "--dlc", "DLC01", "--stage", "L01")
            second = run_progress("status", "--path", str(path), "--dlc", "DLC02", "--stage", "L01")
            self.assertEqual(first.stdout.strip(), "unlocked")
            self.assertEqual(second.stdout.strip(), "unlocked")

    def test_malformed_progress_is_rejected_without_overwrite(self) -> None:
        with tempfile.TemporaryDirectory(dir=TMP_ROOT) as tmp:
            path = Path(tmp) / "progress.json"
            original = "{broken"
            path.write_text(original, encoding="utf-8")
            completed = run_progress("record", "--path", str(path), "--dlc", "DLC01", "--stage", "L01", "--outcome", "stage_clear")
            self.assertEqual(completed.returncode, 2)
            self.assertIn("malformed progress", completed.stderr.lower())
            self.assertEqual(path.read_text(encoding="utf-8"), original)


if __name__ == "__main__":
    unittest.main()
