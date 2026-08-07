from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MENU = ROOT / "scripts" / "game_menu.py"
TMP_ROOT = ROOT / "tests" / ".tmp" / "navigation"
TMP_ROOT.mkdir(parents=True, exist_ok=True)


def run_menu(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(MENU), *args], cwd=ROOT,
                          text=True, encoding="utf-8", capture_output=True, timeout=10)


class NavigationTests(unittest.TestCase):
    def test_tutorial_explains_roles_goal_feedback_boundaries_and_controls(self) -> None:
        completed = run_menu("tutorial")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        for phrase in ("你扮演销售", "Agent 扮演客户和教练", "通过提问", "教练分析", "专业退出", "文字或语音", "暂停", "结束并复盘"):
            self.assertIn(phrase, completed.stdout)

    def test_first_menu_contains_dlcs_but_not_flat_stage_list(self) -> None:
        completed = run_menu("dlcs")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("【1】制造业", completed.stdout)
        self.assertIn("【2】商学院", completed.stdout)
        self.assertNotIn("第一次正式面谈", completed.stdout)

    def test_manufacturing_stage_menu_shows_sequential_lock(self) -> None:
        with tempfile.TemporaryDirectory(dir=TMP_ROOT) as tmp:
            completed = run_menu("stages", "DLC01", "--progress", str(Path(tmp) / "progress.json"))
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("【1】第一次正式面谈　【已解锁】", completed.stdout)
        self.assertIn("【2】三人方案会　【未解锁】", completed.stdout)

    def test_business_school_first_stage_is_available_without_manufacturing_pass(self) -> None:
        with tempfile.TemporaryDirectory(dir=TMP_ROOT) as tmp:
            completed = run_menu("stages", "DLC02", "--progress", str(Path(tmp) / "progress.json"))
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("【1】潜在学员需求诊断　【已解锁】", completed.stdout)

    def test_locked_stage_selection_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(dir=TMP_ROOT) as tmp:
            completed = run_menu("select", "DLC01", "L02", "--progress", str(Path(tmp) / "progress.json"))
        self.assertEqual(completed.returncode, 2)
        self.assertIn("【未解锁】", completed.stdout)


if __name__ == "__main__":
    unittest.main()
