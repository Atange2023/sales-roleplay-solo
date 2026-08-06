# -*- coding: utf-8 -*-
"""Versioned session records and independent learner/customer outcomes."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Mapping, Sequence

DIMENSIONS = (
    "intent_permission",
    "listening",
    "specificity",
    "causal_inquiry",
    "four_stage_diagnosis",
    "solution_fit",
    "decision_next_step",
    "ethics_aftercare",
)


def _validated_scores(scores: Mapping[str, int]) -> dict[str, int]:
    if set(scores) != set(DIMENSIONS):
        missing = sorted(set(DIMENSIONS) - set(scores))
        extra = sorted(set(scores) - set(DIMENSIONS))
        raise ValueError(f"dimension mismatch; missing={missing}, extra={extra}")
    result = {}
    for name in DIMENSIONS:
        value = int(scores[name])
        if not 0 <= value <= 3:
            raise ValueError(f"{name} must be between 0 and 3")
        result[name] = value
    return result


def build_session(
    *,
    dlc: str,
    stage: str,
    duration_seconds: int,
    dimension_scores: Mapping[str, int],
    customer_outcome: str,
    red_lines: Sequence[str],
    professional_exit: bool,
    ended_at: str | None = None,
    input_modes: Sequence[str] = ("text",),
    notes: str = "",
) -> dict:
    dimensions = _validated_scores(dimension_scores)
    total = sum(dimensions.values())
    red_line_list = list(red_lines)
    if red_line_list:
        learner_outcome, cue = "game_over", "game-over"
    elif professional_exit:
        learner_outcome, cue = "professional_exit", "professional-exit"
    elif total == 24:
        learner_outcome, cue = "stage_clear", "achievement"
    elif total >= 16:
        learner_outcome, cue = "stage_clear", "stage-clear"
    else:
        learner_outcome, cue = "needs_practice", "game-over"
    return {
        "schema_version": "1.0",
        "ended_at": ended_at or datetime.now().astimezone().isoformat(timespec="seconds"),
        "dlc": dlc,
        "stage": stage,
        "duration_seconds": max(0, int(duration_seconds)),
        "input_modes": list(dict.fromkeys(input_modes)),
        "capability": {
            "dimensions": dimensions,
            "total": total,
            "maximum": 24,
        },
        "customer_outcome": customer_outcome,
        "learner_outcome": learner_outcome,
        "professional_exit": bool(professional_exit),
        "red_lines": red_line_list,
        "cue": cue,
        "notes": notes,
    }


def append_session(path: Path | str, record: Mapping) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
    return destination