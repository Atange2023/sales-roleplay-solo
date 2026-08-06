from __future__ import annotations

import importlib.util
import unittest
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENGINE_PATH = ROOT / "scripts" / "session_engine.py"
REPORT_PATH = ROOT / "scripts" / "report.py"
TMP_ROOT = ROOT / "tests" / ".tmp" / "sessions"
TMP_ROOT.mkdir(parents=True, exist_ok=True)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class SessionTests(unittest.TestCase):
    def test_customer_refusal_can_be_a_professional_exit_pass(self) -> None:
        self.assertTrue(ENGINE_PATH.is_file(), "session engine is missing")
        engine = load_module(ENGINE_PATH, "session_engine")
        record = engine.build_session(
            dlc="manufacturing",
            stage="L01",
            duration_seconds=420,
            dimension_scores={
                "intent_permission": 3,
                "listening": 3,
                "specificity": 2,
                "causal_inquiry": 2,
                "four_stage_diagnosis": 2,
                "solution_fit": 2,
                "decision_next_step": 3,
                "ethics_aftercare": 3,
            },
            customer_outcome="refused",
            red_lines=[],
            professional_exit=True,
        )
        self.assertEqual(len(record["capability"]["dimensions"]), 8)
        self.assertEqual(record["capability"]["total"], 20)
        self.assertEqual(record["customer_outcome"], "refused")
        self.assertEqual(record["learner_outcome"], "professional_exit")
        self.assertEqual(record["cue"], "professional-exit")

    def test_real_red_line_is_game_over_even_if_customer_advances(self) -> None:
        self.assertTrue(ENGINE_PATH.is_file(), "session engine is missing")
        engine = load_module(ENGINE_PATH, "session_engine_red")
        record = engine.build_session(
            dlc="business-school",
            stage="L01",
            duration_seconds=180,
            dimension_scores={name: 3 for name in engine.DIMENSIONS},
            customer_outcome="advanced",
            red_lines=["pressed_after_clear_refusal"],
            professional_exit=False,
        )
        self.assertEqual(record["customer_outcome"], "advanced")
        self.assertEqual(record["learner_outcome"], "game_over")
        self.assertEqual(record["cue"], "game-over")

    def test_jsonl_log_exports_utf8_weekly_html_and_csv(self) -> None:
        self.assertTrue(ENGINE_PATH.is_file(), "session engine is missing")
        self.assertTrue(REPORT_PATH.is_file(), "report exporter is missing")
        engine = load_module(ENGINE_PATH, "session_engine_log")
        report = load_module(REPORT_PATH, "report")
        base = TMP_ROOT
        base.mkdir(parents=True, exist_ok=True)
        log = base / "sessions.jsonl"
        log.write_text("", encoding="utf-8")
        score_vectors = (
            dict(zip(engine.DIMENSIONS, (2, 2, 2, 2, 1, 1, 1, 1))),
            dict(zip(engine.DIMENSIONS, (3, 3, 2, 2, 2, 2, 2, 2))),
        )
        for idx, scores in enumerate(score_vectors, 1):
            record = engine.build_session(
                dlc="manufacturing",
                stage=f"L0{idx}",
                duration_seconds=300 + idx,
                dimension_scores=scores,
                customer_outcome="delayed",
                red_lines=[],
                professional_exit=False,
                ended_at=f"2026-08-0{idx}T12:00:00+08:00",
            )
            engine.append_session(log, record)
        outputs = report.export_weekly(log, base / "weekly", end_date=date(2026, 8, 7))
        csv_text = outputs["csv"].read_text(encoding="utf-8-sig")
        html_text = outputs["html"].read_text(encoding="utf-8")
        self.assertIn("18", csv_text)
        self.assertIn("训练周报", html_text)
        self.assertIn("↑", html_text)
        self.assertEqual(len(log.read_text(encoding="utf-8").splitlines()), 2)


if __name__ == "__main__":
    unittest.main()