from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "scripts" / "simulator_state.py"


def load_state_module():
    spec = importlib.util.spec_from_file_location("simulator_state", STATE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class SimulatorStateTests(unittest.TestCase):
    def test_non_turn_commands_never_consume_an_effective_turn(self) -> None:
        state_module = load_state_module()
        state = state_module.new_session("正常")
        for command in ("查看任务", "查看规则", "查看权限", "暂停", "继续", "结束并复盘", "/voice", "/text"):
            state = state_module.apply_turn(state, command=command)
        self.assertEqual(state["effective_turns"], 0)
        self.assertEqual(state["quality_counts"], {"high": 0, "medium": 0, "low": 0})

    def test_turn_15_and_18_warn_and_turn_20_forces_timeout(self) -> None:
        state_module = load_state_module()
        state = state_module.new_session("正常")
        warnings = {}
        for turn in range(1, 21):
            state = state_module.apply_turn(state, quality="medium")
            warnings[turn] = list(state["events"])
        self.assertIn("进入收束阶段", warnings[15])
        self.assertIn("仅剩三个有效回合", warnings[18])
        self.assertTrue(state["timeout"])
        self.assertEqual(state["learner_outcome"], "推进超时")
        self.assertEqual(state["customer_outcome"], "态度未明确")
        with self.assertRaises(ValueError):
            state_module.apply_turn(state, quality="high")

    def test_easy_three_high_turns_trigger_two_turn_impulse_but_not_policy_override(self) -> None:
        state_module = load_state_module()
        state = state_module.new_session("简单")
        for _ in range(3):
            state = state_module.apply_turn(state, quality="high")
        self.assertEqual(state["mood"], "impulse")
        self.assertEqual(state["mood_turns_remaining"], 2)
        self.assertIn("客户决策热度上升", state["events"])
        self.assertFalse(state["policy_override"])
        state = state_module.apply_turn(state, quality="medium")
        self.assertEqual(state["mood_turns_remaining"], 1)
        state = state_module.apply_turn(state, quality="medium")
        self.assertEqual(state["mood"], "neutral")

    def test_easy_low_turn_ends_impulse_immediately(self) -> None:
        state_module = load_state_module()
        state = state_module.new_session("简单")
        for quality in ("high", "high", "high", "low"):
            state = state_module.apply_turn(state, quality=quality)
        self.assertEqual(state["mood"], "neutral")
        self.assertEqual(state["high_streak"], 0)
        self.assertEqual(state["low_streak"], 1)

    def test_hard_two_low_turns_trigger_low_mood_and_high_recovers(self) -> None:
        state_module = load_state_module()
        state = state_module.new_session("困难")
        state = state_module.apply_turn(state, quality="low")
        state = state_module.apply_turn(state, quality="low")
        self.assertEqual(state["mood"], "low_mood")
        self.assertIn("客户沟通意愿下降", state["events"])
        state = state_module.apply_turn(state, quality="medium")
        self.assertEqual(state["mood"], "low_mood")
        state = state_module.apply_turn(state, quality="low")
        self.assertIn("未通关风险上升", state["events"])
        state = state_module.apply_turn(state, quality="high")
        self.assertEqual(state["mood"], "neutral")

    def test_normal_difficulty_has_no_mood_acceleration(self) -> None:
        state_module = load_state_module()
        state = state_module.new_session("正常")
        for quality in ("high", "high", "high", "low", "low"):
            state = state_module.apply_turn(state, quality=quality)
        self.assertEqual(state["mood"], "neutral")
        self.assertEqual(state["mood_triggers"], {"impulse": 0, "low_mood": 0})

    def test_severe_violation_resolves_immediately(self) -> None:
        state_module = load_state_module()
        state = state_module.apply_turn(
            state_module.new_session("简单"), quality="high", severe_violation="承诺任何时候退款"
        )
        self.assertEqual(state["learner_outcome"], "彻底失败")
        self.assertEqual(state["customer_outcome"], "关系受损")
        self.assertEqual(state["violations"], ["承诺任何时候退款"])


if __name__ == "__main__":
    unittest.main()
