# -*- coding: utf-8 -*-
"""Deterministic turn, difficulty, and mood state for Agent-native roleplay."""

from __future__ import annotations

from copy import deepcopy


DIFFICULTIES = ("简单", "正常", "困难")
QUALITIES = ("high", "medium", "low")
NON_TURN_COMMANDS = {"查看任务", "查看规则", "查看权限", "暂停", "继续", "结束并复盘", "/voice", "/text"}
MAXIMUM_EFFECTIVE_TURNS = 20


def new_session(difficulty: str = "正常") -> dict:
    if difficulty not in DIFFICULTIES:
        raise ValueError(f"未知难度：{difficulty}")
    return {
        "difficulty": difficulty,
        "effective_turns": 0,
        "maximum_effective_turns": MAXIMUM_EFFECTIVE_TURNS,
        "quality_counts": {"high": 0, "medium": 0, "low": 0},
        "high_streak": 0,
        "low_streak": 0,
        "longest_high_streak": 0,
        "longest_low_streak": 0,
        "mood": "neutral",
        "mood_turns_remaining": 0,
        "mood_triggers": {"impulse": 0, "low_mood": 0},
        "policy_override": False,
        "timeout": False,
        "learner_outcome": None,
        "customer_outcome": None,
        "violations": [],
        "events": [],
    }


def _apply_streaks(state: dict, quality: str) -> None:
    if quality == "high":
        state["high_streak"] += 1
        state["low_streak"] = 0
    elif quality == "low":
        state["low_streak"] += 1
        state["high_streak"] = 0
    else:
        state["high_streak"] = 0
        state["low_streak"] = 0
    state["longest_high_streak"] = max(state["longest_high_streak"], state["high_streak"])
    state["longest_low_streak"] = max(state["longest_low_streak"], state["low_streak"])


def _apply_mood(state: dict, quality: str) -> None:
    difficulty = state["difficulty"]
    if difficulty == "正常":
        state["mood"] = "neutral"
        state["mood_turns_remaining"] = 0
        return

    if difficulty == "简单":
        if state["mood"] == "impulse":
            if quality == "low":
                state["mood"] = "neutral"
                state["mood_turns_remaining"] = 0
            else:
                state["mood_turns_remaining"] -= 1
                if state["mood_turns_remaining"] <= 0:
                    state["mood"] = "neutral"
                    state["mood_turns_remaining"] = 0
        elif quality == "high" and state["high_streak"] >= 3:
            state["mood"] = "impulse"
            state["mood_turns_remaining"] = 2
            state["mood_triggers"]["impulse"] += 1
            state["events"].append("客户决策热度上升")
        return

    if state["mood"] == "low_mood":
        if quality == "high":
            state["mood"] = "neutral"
            state["mood_turns_remaining"] = 0
            state["events"].append("客户沟通意愿恢复")
        elif quality == "low":
            state["events"].append("未通关风险上升")
    elif quality == "low" and state["low_streak"] >= 2:
        state["mood"] = "low_mood"
        state["mood_triggers"]["low_mood"] += 1
        state["events"].append("客户沟通意愿下降")


def apply_turn(
    state: dict,
    *,
    quality: str | None = None,
    command: str | None = None,
    severe_violation: str | None = None,
    learner_outcome: str | None = None,
    customer_outcome: str | None = None,
) -> dict:
    """Return a copied state after one command or effective learner turn."""
    result = deepcopy(state)
    result["events"] = []
    if result.get("learner_outcome") is not None:
        raise ValueError("本局已经结束")
    if command is not None:
        if command not in NON_TURN_COMMANDS:
            raise ValueError(f"未知指令：{command}")
        result["events"].append(f"已执行：{command}")
        return result
    if quality not in QUALITIES:
        raise ValueError("有效回合必须提供 high、medium 或 low 质量")
    if result["effective_turns"] >= result["maximum_effective_turns"]:
        raise ValueError("已达到最大有效回合数")

    result["effective_turns"] += 1
    result["quality_counts"][quality] += 1
    _apply_streaks(result, quality)

    if severe_violation:
        result["violations"].append(severe_violation)
        result["learner_outcome"] = "彻底失败"
        result["customer_outcome"] = "关系受损"
        result["events"].append("触发严重违规，本局结束")
        return result

    _apply_mood(result, quality)
    if result["effective_turns"] == 15:
        result["events"].append("进入收束阶段")
    if result["effective_turns"] == 18:
        result["events"].append("仅剩三个有效回合")

    if learner_outcome is not None:
        result["learner_outcome"] = learner_outcome
        result["customer_outcome"] = customer_outcome
    elif result["effective_turns"] == result["maximum_effective_turns"]:
        result["timeout"] = True
        result["learner_outcome"] = "推进超时"
        result["customer_outcome"] = "态度未明确"
        result["events"].append("有效回合已用完，本局结束")
    return result
