from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "roleplay.py"
TMP_ROOT = ROOT / "tests" / ".tmp" / "cli"
TMP_ROOT.mkdir(parents=True, exist_ok=True)


class OfflineCliTests(unittest.TestCase):
    def test_default_cli_refuses_standalone_roleplay(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(CLI), "--offline", "--no-audio"],
            cwd=ROOT,
            input="",
            text=True,
            encoding="utf-8",
            capture_output=True,
            timeout=10,
        )
        self.assertEqual(completed.returncode, 2, completed.stderr)
        self.assertIn("HOST AGENT REQUIRED", completed.stdout)
        self.assertNotIn("SELECT DLC", completed.stdout)

    def test_smoke_flow_runs_offline_and_exports_weekly_report(self) -> None:
        log = TMP_ROOT / "sessions.jsonl"
        reports = TMP_ROOT / "reports"
        log.write_text("", encoding="utf-8")
        completed = subprocess.run(
            [
                sys.executable,
                str(CLI),
                "--smoke",
                "--offline",
                "--no-audio",
                "--log",
                str(log),
                "--report-dir",
                str(reports),
            ],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            capture_output=True,
            timeout=20,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("SALES ROLEPLAY SOLO v0.4", completed.stdout)
        self.assertIn("PROFESSIONAL EXIT", completed.stdout)
        record = json.loads(log.read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(record["customer_outcome"], "refused")
        self.assertEqual(record["learner_outcome"], "professional_exit")
        self.assertTrue((reports / "weekly-report.html").is_file())
        self.assertTrue((reports / "weekly-report.csv").is_file())


if __name__ == "__main__":
    unittest.main()
