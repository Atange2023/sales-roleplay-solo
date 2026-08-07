# -*- coding: utf-8 -*-
"""Versioned session records and independent learner/customer outcomes."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Mapping, Sequence

DIMENSIONS = ("intent_permission", "listening", "specificity", "causal_inquiry", "four_stage_diagnosis", "solution_fit", "decision_next_step", "ethics_aftercare")
DIFFICULTIES = ("简单", "正常", "困难")


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


def _simulation_record(
    difficulty: str, effective_turns: int, quality_counts: Mapping[str, int] | None,
    longest_high_streak: int, longest_low_streak: int,
    mood_triggers: Mapping[str, int] | None, timeout: bool,
) -> dict:
    if difficulty not in DIFFICULTIES:
        raise ValueError(f"unknown difficulty: {difficulty}")
    turn_count = int(effective_turns)
    if not 0 <= turn_count <= 20:
        raise ValueError("effective_turns must be between 0 and 20")
    counts = dict(quality_counts or {"high": 0, "medium": 0, "low": 0})
    if set(counts) != {"high", "medium", "low"} or any(int(value) < 0 for value in counts.values()):
        raise ValueError("quality_counts must contain nonnegative high, medium, and low values")
    counts = {name: int(counts[name]) for name in ("high", "medium", "low")}
    if sum(counts.values()) != turn_count:
        raise ValueError("quality_counts must sum to effective_turns")
    triggers = dict(mood_triggers or {"impulse": 0, "low_mood": 0})
    if set(triggers) != {"impulse", "low_mood"} or any(int(value) < 0 for value in triggers.values()):
        raise ValueError("mood_triggers must contain nonnegative impulse and low_mood values")
    return {
        "difficulty": difficulty,
        "effective_turns": turn_count,
        "maximum_effective_turns": 20,
        "quality_counts": counts,
        "longest_high_streak": max(0, int(longest_high_streak)),
        "longest_low_streak": max(0, int(longest_low_streak)),
        "mood_triggers": {name: int(triggers[name]) for name in ("impulse", "low_mood")},
        "timeout": bool(timeout),
    }


def build_session(
    *, dlc: str, stage: str, duration_seconds: int,
    dimension_scores: Mapping[str, int], customer_outcome: str,
    red_lines: Sequence[str], professional_exit: bool,
    ended_at: str | None = None, input_modes: Sequence[str] = ("text",), notes: str = "",
    difficulty: str = "正常", effective_turns: int = 0,
    quality_counts: Mapping[str, int] | None = None,
    longest_high_streak: int = 0, longest_low_streak: int = 0,
    mood_triggers: Mapping[str, int] | None = None, timeout: bool = False,
    profile_reconstruction: Mapping | None = None,
    policy_negotiation: Mapping | None = None,
    learner_outcome_override: str | None = None,
) -> dict:
    dimensions = _validated_scores(dimension_scores)
    total = sum(dimensions.values())
    red_line_list = list(red_lines)
    if red_line_list:
        learner_outcome, cue = "game_over", "game-over"
    elif professional_exit:
        learner_outcome, cue = "professional_exit", "professional-exit"
    elif timeout:
        learner_outcome, cue = "推进超时", "game-over"
    elif total == 24:
        learner_outcome, cue = "stage_clear", "achievement"
    elif total >= 16:
        learner_outcome, cue = "stage_clear", "stage-clear"
    else:
        learner_outcome, cue = "needs_practice", "game-over"
    if learner_outcome_override:
        learner_outcome = learner_outcome_override
        if learner_outcome_override in {"通关", "正常报名", "奖学金流程", "助学金流程", "特殊条件审批"}:
            cue = "stage-clear"
    record = {
        "schema_version": "1.1",
        "ended_at": ended_at or datetime.now().astimezone().isoformat(timespec="seconds"),
        "dlc": dlc, "stage": stage, "duration_seconds": max(0, int(duration_seconds)),
        "input_modes": list(dict.fromkeys(input_modes)),
        "capability": {"dimensions": dimensions, "total": total, "maximum": 24},
        "customer_outcome": customer_outcome, "learner_outcome": learner_outcome,
        "professional_exit": bool(professional_exit), "red_lines": red_line_list,
        "cue": cue, "notes": notes,
        "simulation": _simulation_record(
            difficulty, effective_turns, quality_counts, longest_high_streak,
            longest_low_streak, mood_triggers, timeout,
        ),
    }
    if profile_reconstruction is not None:
        record["profile_reconstruction"] = dict(profile_reconstruction)
    if policy_negotiation is not None:
        record["policy_negotiation"] = dict(policy_negotiation)
    return record


def append_session(path: Path | str, record: Mapping) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
    return destination
