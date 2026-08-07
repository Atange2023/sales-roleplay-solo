# -*- coding: utf-8 -*-
"""Deterministic outcome and scoring rules for DLC02 stages."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

EVIDENCE_FIELDS = (
    "identity", "attendance_source", "interest_trigger", "current_situation",
    "recent_problem", "impact", "desired_goal", "past_attempts", "past_learning",
    "time_conditions", "funding_conditions", "decision_makers", "concerns",
    "acceptable_next_step", "boundaries",
)
PROFILE_DIMENSIONS = (
    "real_need", "urgency", "goal_clarity", "subjective_motivation",
    "time_readiness", "funding_readiness", "decision_readiness",
    "paid_value_orientation",
)
L01_PASS_TRACKS = (
    "application_form", "formal_trial", "professor_consultation",
    "school_leadership_consultation", "academic_topic_consultation",
    "admissions_followup", "external_relations_consultation",
    "qualification_preassessment", "decision_maker_joint_consultation",
)
NEXT_ACTION_FIELDS = ("counterpart", "purpose", "time_window", "explicit_consent", "contact_permission")

POLICY_SCORE_DIMENSIONS = (
    "concern_diagnosis", "policy_accuracy", "authority_boundary", "risk_disclosure",
    "value_price", "compliant_option", "negotiation_stability", "compliant_close",
)
IMMEDIATE_FAILURE_CODES = (
    "refund_anytime", "guaranteed_scholarship", "guaranteed_aid",
    "private_discount_or_rebate", "concealed_refund_limit", "register_then_refund",
    "falsified_policy", "guaranteed_outcome", "fake_invoice",
)


def load_personas() -> dict:
    return json.loads((ASSETS / "dlc02-personas.json").read_text(encoding="utf-8"))


def load_school_policy() -> dict:
    return json.loads((ASSETS / "dlc02-school-policy.json").read_text(encoding="utf-8"))


def _l01_result(outcome: str, *, passed: bool = False) -> dict:
    return {
        "learner_outcome": outcome,
        "progress_outcome": "stage_clear" if passed else ("professional_exit" if outcome == "专业收场" else "needs_practice"),
        "unlock_next_stage": passed,
    }


def _qualified_next_action(next_action: Mapping | None) -> bool:
    if not next_action or next_action.get("track") not in L01_PASS_TRACKS:
        return False
    return all(bool(next_action.get(field)) for field in NEXT_ACTION_FIELDS)


def evaluate_l01_outcome(
    *, next_action: Mapping | None = None, real_need: bool = False,
    readiness_blocked: bool = False, motivation_weak: bool = False,
    information_unverified: bool = False, freebie_count: int = 0,
    paid_intent: bool = True, professional_close: bool = False,
    explicit_aversion: bool = False, timeout: bool = False,
) -> dict:
    if timeout:
        return _l01_result("推进超时")
    if explicit_aversion:
        return _l01_result("彻底失败")
    if professional_close:
        return _l01_result("专业收场")
    if _qualified_next_action(next_action):
        return _l01_result("通关", passed=True)
    if freebie_count >= 3 and not paid_intent:
        return _l01_result("未通关·低价值索取")
    if motivation_weak:
        return _l01_result("未通关·动力不足")
    if real_need and readiness_blocked:
        return _l01_result("未通关·可培育")
    if information_unverified or next_action:
        return _l01_result("未通关·信息不足")
    return _l01_result("未通关·信息不足")


def _validate_score_vector(vector: Mapping[str, int], dimensions: Sequence[str]) -> dict[str, int]:
    if set(vector) != set(dimensions):
        raise ValueError("评分维度不完整")
    result = {name: int(vector[name]) for name in dimensions}
    if any(value < 0 or value > 3 for value in result.values()):
        raise ValueError("每个评分维度必须为 0 到 3")
    return result


def score_profile_estimate(
    truth: Mapping[str, int], estimate: Mapping[str, int], discovered_evidence: Sequence[str],
    citations: Mapping[str, str] | None = None, *, ending: str,
) -> dict:
    truth_scores = _validate_score_vector(truth, PROFILE_DIMENSIONS)
    estimate_scores = _validate_score_vector(estimate, PROFILE_DIMENSIONS)
    discovered = set(discovered_evidence)
    unknown = discovered - set(EVIDENCE_FIELDS)
    if unknown:
        raise ValueError(f"未知证据项：{sorted(unknown)}")
    citation_map = dict(citations or {})
    rows = []
    total = 0
    for name in PROFILE_DIMENSIONS:
        difference = estimate_scores[name] - truth_scores[name]
        accuracy = 3 - abs(difference)
        total += accuracy
        rows.append({
            "name": name, "truth": truth_scores[name], "estimate": estimate_scores[name],
            "difference": difference, "accuracy": accuracy, "evidence": citation_map.get(name, "未引用"),
        })
    return {
        "ending": ending,
        "evidence_discovered": len(discovered),
        "evidence_total": len(EVIDENCE_FIELDS),
        "evidence_completeness_percent": round(len(discovered) * 100 / len(EVIDENCE_FIELDS)),
        "profile_accuracy": {"dimensions": rows, "total": total, "maximum": 24},
    }


def _l02_result(outcome: str, *, passed: bool = False, red_lines: Sequence[str] = ()) -> dict:
    return {"learner_outcome": outcome, "stage_passed": passed, "red_lines": list(red_lines)}


def validate_special_condition(
    *, condition_specific: bool, condition_lawful: bool, customer_commitment: bool,
    authority: str | None, made_promise: bool,
) -> bool:
    return all((condition_specific, condition_lawful, customer_commitment, authority == "school_leadership", not made_promise))


def evaluate_l02_outcome(
    *, route: str | None = None, customer_commitment: bool = False,
    formal_submission: bool = False, authority: str | None = None,
    made_promise: bool = False, condition_specific: bool = False,
    condition_lawful: bool = False, violations: Sequence[str] = (),
    mood: str = "neutral", considering: bool = False, information_only: bool = False,
    unresolved_stakeholder: bool = False, professional_close: bool = False,
    rejected: bool = False, timeout: bool = False,
) -> dict:
    del mood  # Mood may accelerate a decision, never alter the policy gate.
    red_lines = [code for code in violations if code in IMMEDIATE_FAILURE_CODES]
    if red_lines:
        return _l02_result("彻底失败", red_lines=red_lines)
    if timeout:
        return _l02_result("推进超时")
    if rejected:
        return _l02_result("彻底失败")
    if professional_close:
        return _l02_result("专业收场")

    if route == "normal_registration" and customer_commitment and formal_submission and authority in {"admissions", "finance_admin"} and not made_promise:
        return _l02_result("正常报名", passed=True)
    if route == "scholarship_application" and customer_commitment and formal_submission and authority == "scholarship_committee" and not made_promise:
        return _l02_result("奖学金流程", passed=True)
    if route == "aid_application" and customer_commitment and formal_submission and authority == "academic_center" and not made_promise:
        return _l02_result("助学金流程", passed=True)
    if route == "special_approval":
        if formal_submission and validate_special_condition(
            condition_specific=condition_specific, condition_lawful=condition_lawful,
            customer_commitment=customer_commitment, authority=authority, made_promise=made_promise,
        ):
            return _l02_result("特殊条件审批", passed=True)
        return _l02_result("未通关·条件未闭环")
    if considering:
        return _l02_result("未通关·继续考虑")
    if information_only:
        return _l02_result("未通关·仅了解信息")
    if unresolved_stakeholder:
        return _l02_result("未通关·关键条件未解决")
    return _l02_result("未通关·条件未闭环")


def score_policy_negotiation(scores: Mapping[str, int]) -> dict:
    dimensions = _validate_score_vector(scores, POLICY_SCORE_DIMENSIONS)
    return {"dimensions": dimensions, "total": sum(dimensions.values()), "maximum": 24}


def render_l02_briefing() -> str:
    return """╔════════════ 恭喜晋级 ════════════╗
【背景】潜在学员已完成前期沟通，现在与你确认报名、费用或申请细节。
【学校规则】付款后仅在正式注册前有五个自然日冷静期；正式注册后原则上不退款。奖学金与助学金必须按流程申请，招生老师不得承诺结果或私自优惠。
【职责权限】
- 招生老师：解释标准规则、收集材料、推进流程。
- 财务与教务：确认费用、付款、注册、冷静期、退款与延期。
- 奖学金委员会：决定奖学金资格、比例与金额。
- 学术中心主任或教授：决定助学金与学术支持。
- 校领导：审批特殊支付、资源合作与例外条件。
【通关目标】在不越权、不作虚假承诺的前提下，推进正常报名、奖学金申请、助学金申请或特殊条件审批。
╚══════════════════════════════════╝"""
