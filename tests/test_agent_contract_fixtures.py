from __future__ import annotations

import json
import unittest
from pathlib import Path


CASES = Path(__file__).resolve().parent / "agent-evals" / "cases.json"


class AgentContractFixtureTests(unittest.TestCase):
    def test_six_unique_behavior_cases_are_complete(self) -> None:
        payload = json.loads(CASES.read_text(encoding="utf-8"))
        cases = payload["cases"]
        ids = [case["id"] for case in cases]
        self.assertEqual(len(cases), 6)
        self.assertEqual(len(ids), len(set(ids)))
        for case in cases:
            self.assertTrue(case["prompt"])
            self.assertTrue(case["must"])
            self.assertTrue(case["must_not"])


if __name__ == "__main__":
    unittest.main()
