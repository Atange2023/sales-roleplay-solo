from __future__ import annotations

import importlib.util
import unittest
import uuid
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENGINE_PATH = ROOT / "scripts" / "session_engine.py"
REPORT_PATH = ROOT / "scripts" / "report.py"
TMP_ROOT = ROOT / "tests" / ".tmp" / "sessions-v043"
TMP_ROOT.mkdir(parents=True, exist_ok=True)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class SessionV043Tests(unittest.TestCase):
    def test_new_simulation_and_stage_scores_are_stored_additively(self) -> None:
        engine = load_module(ENGINE_PATH, "session_engine_v043")
        profile = {"evidence_completeness_percent": 80, "profile_accuracy": {"total": 21, "maximum": 24}}
        policy = {"total": 20, "maximum": 24, "dimensions": {"policy_accuracy": 3}}
        record = engine.build_session(
            dlc="DLC02", stage="L02", duration_seconds=720,
            dimension_scores={name: 2 for name in engine.DIMENSIONS},
            customer_outcome="conditional_commitment", red_lines=[], professional_exit=False,
            difficulty="困难", effective_turns=18,
            quality_counts={"high": 7, "medium": 8, "low": 3},
            longest_high_streak=3, longest_low_streak=2,
            mood_triggers={"impulse": 0, "low_mood": 1}, timeout=False,
            profile_reconstruction=profile, policy_negotiation=policy,
            learner_outcome_override="特殊条件审批",
        )
        self.assertEqual(record["schema_version"], "1.1")
        self.assertEqual(record["simulation"]["difficulty"], "困难")
        self.assertEqual(record["simulation"]["effective_turns"], 18)
        self.assertEqual(record["simulation"]["quality_counts"]["low"], 3)
        self.assertEqual(record["simulation"]["mood_triggers"]["low_mood"], 1)
        self.assertEqual(record["profile_reconstruction"]["profile_accuracy"]["total"], 21)
        self.assertEqual(record["policy_negotiation"]["total"], 20)
        self.assertEqual(record["learner_outcome"], "特殊条件审批")

    def test_weekly_exports_include_new_fields_and_accept_old_records(self) -> None:
        engine = load_module(ENGINE_PATH, "session_engine_v043_export")
        report = load_module(REPORT_PATH, "report_v043")
        token = uuid.uuid4().hex
        log = TMP_ROOT / f"{token}.jsonl"
        output = TMP_ROOT / token
        old_record = engine.build_session(
            dlc="DLC01", stage="L01", duration_seconds=60,
            dimension_scores={name: 2 for name in engine.DIMENSIONS}, customer_outcome="followup",
            red_lines=[], professional_exit=False, ended_at="2026-08-06T10:00:00+08:00",
        )
        old_record.pop("simulation", None)
        engine.append_session(log, old_record)
        engine.append_session(log, engine.build_session(
            dlc="DLC02", stage="L01", duration_seconds=600,
            dimension_scores={name: 3 for name in engine.DIMENSIONS}, customer_outcome="advanced",
            red_lines=[], professional_exit=False, ended_at="2026-08-07T10:00:00+08:00",
            difficulty="简单", effective_turns=12, quality_counts={"high": 8, "medium": 4, "low": 0},
            mood_triggers={"impulse": 1, "low_mood": 0},
        ))
        outputs = report.export_weekly(log, output, end_date=date(2026, 8, 7))
        csv_text = outputs["csv"].read_text(encoding="utf-8-sig")
        html_text = outputs["html"].read_text(encoding="utf-8")
        for column in ("difficulty", "effective_turns", "high_quality_turns", "timeout"):
            self.assertIn(column, csv_text)
        self.assertIn("简单", csv_text)
        self.assertIn("难度", html_text)
        self.assertIn("有效回合", html_text)


if __name__ == "__main__":
    unittest.main()
