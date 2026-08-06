from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class V03InheritanceTests(unittest.TestCase):
    def test_all_legacy_audio_files_remain_nonempty(self) -> None:
        expected = {"audio": 51, "audio3": 48, "audio4": 46}
        for folder, count in expected.items():
            files = sorted((ROOT / folder).glob("*.mp3"))
            self.assertEqual(len(files), count, folder)
            self.assertTrue(all(path.stat().st_size > 1_000 for path in files), folder)

    def test_all_three_v03_dialogue_databases_remain_parseable(self) -> None:
        names = (
            "zhang_dialogue.json",
            "three_party_dialogue.json",
            "business_school_dialogue.json",
        )
        for name in names:
            data = json.loads((ROOT / "scenarios" / name).read_text(encoding="utf-8"))
            self.assertTrue(data.get("openings") or data.get("branches"), name)

    def test_training_manuals_reviews_methods_and_scenarios_remain(self) -> None:
        required = (
            "docs/usage_manual.md",
            "docs/level_system.md",
            "docs/review_template.md",
            "docs/example_review_three_party.md",
            "docs/example_review_business_school.md",
            "methods/references/open-with-questions.md",
            "methods/references/master-questions.md",
            "methods/references/handle-rejection.md",
            "methods/references/four-step-advance.md",
            "methods/references/close-and-followup.md",
            "scenarios/zhang_script.md",
            "scenarios/three_party_script.md",
            "scenarios/business_school_script.md",
        )
        for relative in required:
            path = ROOT / relative
            self.assertTrue(path.is_file(), relative)
            self.assertGreater(path.stat().st_size, 100, relative)


if __name__ == "__main__":
    unittest.main()
