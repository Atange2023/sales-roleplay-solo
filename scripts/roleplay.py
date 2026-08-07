# -*- coding: utf-8 -*-
"""Support and validation commands for the Agent-native Skill.

The host Agent is the conversation engine. This module deliberately refuses
to start a learner-facing roleplay loop, preventing fallback to canned replies.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from report import export_weekly
from session_engine import append_session, build_session

BANNER = r"""
+=====================================================+
|        SALES ROLEPLAY SOLO v0.4.3 // OFFLINE       |
|        AGENT-NATIVE SUPPORT VALIDATION TERMINAL     |
+=====================================================+
"""

DEFAULT_SCORES = {
    "intent_permission": 3,
    "listening": 3,
    "specificity": 2,
    "causal_inquiry": 2,
    "four_stage_diagnosis": 2,
    "solution_fit": 2,
    "decision_next_step": 3,
    "ethics_aftercare": 3,
}


def smoke(log: Path, report_dir: Path, no_audio: bool) -> int:
    """Validate local assets, logging, and report export without roleplaying."""
    print(BANNER)
    print("[CUE] assets/cues/boot.wav" if not no_audio else "[CUE CHECK] boot")
    print("[DLC] DLC01  [STAGE] L01")
    print("[VALIDATION FIXTURE] customer outcome=refused")
    record = build_session(
        dlc="DLC01",
        stage="L01",
        duration_seconds=90,
        dimension_scores=DEFAULT_SCORES,
        customer_outcome="refused",
        red_lines=[],
        professional_exit=True,
        input_modes=("text", "voice"),
        notes="offline support-tool smoke validation",
    )
    append_session(log, record)
    print("[CUE] assets/cues/professional-exit.wav" if not no_audio else "[CUE CHECK] professional-exit")
    print(f"[PROFESSIONAL EXIT] capability={record['capability']['total']}/24 customer=refused")
    export_weekly(log, report_dir, end_date=date.today())
    print(f"[REPORT] {report_dir / 'weekly-report.html'}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Support validation for the Agent-native sales roleplay Skill.")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--no-audio", action="store_true")
    parser.add_argument("--log", type=Path, default=ROOT / "data" / "sessions.jsonl")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    args = parser.parse_args(argv)
    if args.smoke:
        return smoke(args.log, args.report_dir, args.no_audio)
    print("HOST AGENT REQUIRED: load this Skill and conduct the roleplay in the current conversation. Python is support tooling only.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
