from __future__ import annotations

import json
import unittest
from pathlib import Path


CASES = Path(__file__).resolve().parent / "agent-evals" / "cases.json"


class AgentContractFixtureTests(unittest.TestCase):
    def test_v043_behavior_cases_are_complete_and_unique(self) -> None:
        payload = json.loads(CASES.read_text(encoding="utf-8"))
        cases = payload["cases"]
        ids = [case["id"] for case in cases]
        required = {
            "startup_tutorial", "dlc_progression", "semantic_reply_and_coaching",
            "modality_continuity", "professional_close", "three_party_state",
            "l01_profile_reconstruction", "l02_policy_briefing",
            "l02_special_approval", "turn_twenty_timeout", "no_internal_leakage",
        }
        self.assertTrue(required.issubset(ids))
        self.assertEqual(len(ids), len(set(ids)))
        for case in cases:
            self.assertTrue(case["prompt"])
            self.assertTrue(case["must"])
            self.assertTrue(case["must_not"])


if __name__ == "__main__":
    unittest.main()
