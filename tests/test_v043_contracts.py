from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"


def load_json(name: str) -> dict:
    return json.loads((ASSETS / name).read_text(encoding="utf-8"))


class V043ContentContractTests(unittest.TestCase):
    def test_version_and_dlc02_stage_contract_are_v043(self) -> None:
        version = load_json("version.json")
        config = load_json("game-config.json")
        dlc02 = next(item for item in config["dlcs"] if item["id"] == "DLC02")

        self.assertEqual(version["version"], "v0.4.3")
        self.assertEqual(config["session_rules"]["maximum_effective_turns"], 20)
        self.assertEqual(config["session_rules"]["difficulties"], ["简单", "正常", "困难"])
        self.assertEqual(
            [(stage["id"], stage["name"]) for stage in dlc02["stages"]],
            [("L01", "潜在学员需求诊断"), ("L02", "报名政策与价格谈判")],
        )
        self.assertEqual(dlc02["stages"][0]["unlock_outcomes"], ["stage_clear"])

    def test_l01_personas_define_all_reconstruction_truth_dimensions(self) -> None:
        payload = load_json("dlc02-personas.json")
        required = {
            "real_need", "urgency", "goal_clarity", "subjective_motivation",
            "time_readiness", "funding_readiness", "decision_readiness",
            "paid_value_orientation",
        }
        personas = payload["stage1_personas"]
        self.assertGreaterEqual(len(personas), 4)
        for persona in personas:
            self.assertTrue(persona["id"])
            self.assertEqual(set(persona["truth_scores"]), required)
            self.assertTrue(all(0 <= value <= 3 for value in persona["truth_scores"].values()))
            self.assertTrue(persona["opening_text"])
            self.assertEqual(len(persona["evidence"]), 15)

    def test_l02_personas_and_school_policy_cover_negotiation_boundaries(self) -> None:
        personas = load_json("dlc02-personas.json")["stage2_personas"]
        policy = load_json("dlc02-school-policy.json")

        self.assertEqual(
            {item["type"] for item in personas},
            {"老板型", "学霸型", "打工人型", "企业付费型", "资源合作型"},
        )
        self.assertEqual(
            set(policy["pass_routes"]),
            {"normal_registration", "scholarship_application", "aid_application", "special_approval"},
        )
        self.assertEqual(
            set(policy["authorities"]),
            {"admissions", "finance_admin", "scholarship_committee", "academic_center", "school_leadership"},
        )
        self.assertGreaterEqual(len(policy["immediate_failure_promises"]), 7)
        self.assertEqual(policy["cooling_period"]["days"], 5)
        self.assertFalse(policy["cooling_period"]["available_after_registration"])


if __name__ == "__main__":
    unittest.main()
