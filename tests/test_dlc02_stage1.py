from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RULES_PATH = ROOT / "scripts" / "dlc02_rules.py"


def load_rules():
    spec = importlib.util.spec_from_file_location("dlc02_rules_l01", RULES_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def qualified_action(track: str = "professor_consultation") -> dict:
    return {
        "track": track,
        "counterpart": "数字化转型教授",
        "purpose": "讨论跨部门协同课题",
        "time_window": "下周三下午",
        "explicit_consent": True,
        "contact_permission": True,
    }


class Dlc02Stage1Tests(unittest.TestCase):
    def test_only_a_complete_consented_next_action_passes(self) -> None:
        rules = load_rules()
        result = rules.evaluate_l01_outcome(next_action=qualified_action())
        self.assertEqual(result["learner_outcome"], "通关")
        self.assertEqual(result["progress_outcome"], "stage_clear")
        self.assertTrue(result["unlock_next_stage"])

        for missing in ("counterpart", "purpose", "time_window", "explicit_consent", "contact_permission"):
            action = qualified_action()
            action[missing] = False if missing.endswith(("consent", "permission")) else ""
            with self.subTest(missing=missing):
                result = rules.evaluate_l01_outcome(next_action=action)
                self.assertFalse(result["unlock_next_stage"])
                self.assertEqual(result["learner_outcome"], "未通关·信息不足")

    def test_all_supported_next_action_tracks_can_pass(self) -> None:
        rules = load_rules()
        expected = {
            "application_form", "formal_trial", "professor_consultation",
            "school_leadership_consultation", "academic_topic_consultation",
            "admissions_followup", "external_relations_consultation",
            "qualification_preassessment", "decision_maker_joint_consultation",
        }
        self.assertEqual(set(rules.L01_PASS_TRACKS), expected)
        for track in expected:
            with self.subTest(track=track):
                self.assertTrue(rules.evaluate_l01_outcome(next_action=qualified_action(track))["unlock_next_stage"])

    def test_non_pass_and_failure_endings_are_distinct(self) -> None:
        rules = load_rules()
        cases = [
            ({"real_need": True, "readiness_blocked": True}, "未通关·可培育"),
            ({"motivation_weak": True}, "未通关·动力不足"),
            ({"information_unverified": True}, "未通关·信息不足"),
            ({"freebie_count": 3, "paid_intent": False}, "未通关·低价值索取"),
            ({"professional_close": True}, "专业收场"),
            ({"explicit_aversion": True}, "彻底失败"),
            ({"timeout": True}, "推进超时"),
        ]
        for inputs, expected in cases:
            with self.subTest(expected=expected):
                result = rules.evaluate_l01_outcome(**inputs)
                self.assertEqual(result["learner_outcome"], expected)
                self.assertFalse(result["unlock_next_stage"])

    def test_profile_reconstruction_reports_evidence_and_accuracy_for_any_ending(self) -> None:
        rules = load_rules()
        truth = {name: index % 4 for index, name in enumerate(rules.PROFILE_DIMENSIONS)}
        estimate = dict(truth)
        estimate[rules.PROFILE_DIMENSIONS[0]] = min(3, truth[rules.PROFILE_DIMENSIONS[0]] + 1)
        discovered = list(rules.EVIDENCE_FIELDS[:12])
        citations = {name: f"第{index + 1}轮证据" for index, name in enumerate(rules.PROFILE_DIMENSIONS)}

        report = rules.score_profile_estimate(truth, estimate, discovered, citations, ending="彻底失败")
        self.assertEqual(report["ending"], "彻底失败")
        self.assertEqual(report["evidence_discovered"], 12)
        self.assertEqual(report["evidence_total"], 15)
        self.assertEqual(report["evidence_completeness_percent"], 80)
        self.assertEqual(report["profile_accuracy"]["maximum"], 24)
        self.assertEqual(report["profile_accuracy"]["total"], 23)
        self.assertEqual(len(report["profile_accuracy"]["dimensions"]), 8)
        self.assertTrue(all("truth" in row and "estimate" in row and "difference" in row and "evidence" in row for row in report["profile_accuracy"]["dimensions"]))


if __name__ == "__main__":
    unittest.main()
