from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RULES_PATH = ROOT / "scripts" / "dlc02_rules.py"


def load_rules():
    spec = importlib.util.spec_from_file_location("dlc02_rules_l02", RULES_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class Dlc02Stage2Tests(unittest.TestCase):
    def test_standard_scholarship_and_aid_routes_pass_without_promises(self) -> None:
        rules = load_rules()
        cases = [
            ("normal_registration", "finance_admin", "正常报名"),
            ("scholarship_application", "scholarship_committee", "奖学金流程"),
            ("aid_application", "academic_center", "助学金流程"),
        ]
        for route, authority, ending in cases:
            with self.subTest(route=route):
                result = rules.evaluate_l02_outcome(
                    route=route, customer_commitment=True, formal_submission=True,
                    authority=authority, made_promise=False,
                )
                self.assertEqual(result["learner_outcome"], ending)
                self.assertTrue(result["stage_passed"])

    def test_special_approval_requires_specific_lawful_condition_commitment_and_authority(self) -> None:
        rules = load_rules()
        valid = dict(
            route="special_approval", customer_commitment=True, formal_submission=True,
            authority="school_leadership", made_promise=False,
            condition_specific=True, condition_lawful=True,
        )
        result = rules.evaluate_l02_outcome(**valid)
        self.assertEqual(result["learner_outcome"], "特殊条件审批")
        self.assertTrue(result["stage_passed"])

        for key, value in (("customer_commitment", False), ("condition_specific", False), ("condition_lawful", False), ("made_promise", True), ("authority", "admissions")):
            inputs = dict(valid)
            inputs[key] = value
            with self.subTest(key=key):
                result = rules.evaluate_l02_outcome(**inputs)
                self.assertFalse(result["stage_passed"])
                self.assertEqual(result["learner_outcome"], "未通关·条件未闭环")

    def test_immediate_policy_violations_override_customer_commitment_and_easy_impulse(self) -> None:
        rules = load_rules()
        for code in rules.IMMEDIATE_FAILURE_CODES:
            with self.subTest(code=code):
                result = rules.evaluate_l02_outcome(
                    route="normal_registration", customer_commitment=True,
                    formal_submission=True, authority="finance_admin",
                    made_promise=False, violations=[code], mood="impulse",
                )
                self.assertEqual(result["learner_outcome"], "彻底失败")
                self.assertFalse(result["stage_passed"])
                self.assertTrue(result["red_lines"])

    def test_non_pass_endings_remain_distinct(self) -> None:
        rules = load_rules()
        cases = [
            ({"considering": True}, "未通关·继续考虑"),
            ({"information_only": True}, "未通关·仅了解信息"),
            ({"unresolved_stakeholder": True}, "未通关·关键条件未解决"),
            ({"professional_close": True}, "专业收场"),
            ({"rejected": True}, "彻底失败"),
            ({"timeout": True}, "推进超时"),
        ]
        for flags, ending in cases:
            with self.subTest(ending=ending):
                result = rules.evaluate_l02_outcome(**flags)
                self.assertEqual(result["learner_outcome"], ending)
                self.assertFalse(result["stage_passed"])

    def test_policy_negotiation_score_has_eight_dimensions_and_maximum_24(self) -> None:
        rules = load_rules()
        scores = {name: 3 for name in rules.POLICY_SCORE_DIMENSIONS}
        report = rules.score_policy_negotiation(scores)
        self.assertEqual(len(report["dimensions"]), 8)
        self.assertEqual(report["total"], 24)
        self.assertEqual(report["maximum"], 24)
        with self.assertRaises(ValueError):
            rules.score_policy_negotiation({name: 4 for name in rules.POLICY_SCORE_DIMENSIONS})

    def test_stage_briefing_is_complete_chinese_player_information(self) -> None:
        rules = load_rules()
        briefing = rules.render_l02_briefing()
        for phrase in ("恭喜晋级", "背景", "学校规则", "职责权限", "通关目标", "五个自然日", "奖学金委员会", "校领导"):
            self.assertIn(phrase, briefing)
        for leaked in ("JSON", "TTS", "manifest", "内部思考"):
            self.assertNotIn(leaked, briefing)


if __name__ == "__main__":
    unittest.main()
