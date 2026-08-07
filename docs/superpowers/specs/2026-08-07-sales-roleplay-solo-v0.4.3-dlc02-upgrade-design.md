# Sales Roleplay Solo v0.4.3 DLC02 Upgrade Design

**Status:** Approved for implementation  
**Date:** 2026-08-07  
**Version:** v0.4.3  
**Scope:** Chinese DOS/MUD presentation shell, DLC02-L01 upgrade, and new DLC02-L02. All accepted v0.3/v0.4.2 behavior remains a regression requirement.

## 1. Product contract

The host Agent remains the semantic customer and coach. Python is deterministic support for presentation, media, configuration, progression, session state, reports, updates, and tests. No standalone Python dialogue engine is introduced.

The release preserves the 145 v0.3 customer MP3 files, existing fixed lines, five music cues, v0.3 scenario pacing and review depth, per-turn coaching, independent customer/learner outcomes, local logs/reports, offline operation, and portable updates.

## 2. Player-visible presentation

Only the brand title may use English: `SALES ROLEPLAY SOLO`. All status labels and instructions use standard Chinese game language. Player-visible output must not mention TTS, MP3, JSON, manifests, branches, fixed-line matching, model reasoning, scripts, tool calls, or dynamic fallback.

Startup order:

1. Launch the boot cue.
2. Render a DOS/BBS-style monospaced title with `SALES ROLEPLAY SOLO`, `销售实战模拟训练系统`, and `版本 0.4.3`.
3. Show the first-use tutorial.
4. Show numbered DLC choices.
5. After DLC choice, show numbered stages for that DLC.
6. Stage input immediately validates and loads the selected stage. Never ask for an extra phrase such as “开始第一关”.

Status vocabulary is Chinese: `已解锁`, `未解锁`, `已完成`, `重新挑战`, `载入中`, `已就绪`. Loading messages use game language such as `关卡数据载入中` and `教练分析数据载入中`.

Every menu and every playable turn shows:

```text
【输入方式】直接输入文字，或点击麦克风说话
【语音指令】输入 /voice 可启用本机录音
```

When generated voice is needed, show `【语音】客户正在组织语言……`. When voice is unavailable, show `【提示】本轮语音暂不可用，已自动切换为文字，不影响关卡进度。`

## 3. Menu and difficulty input

The stage menu does not add a separate difficulty screen. A stage row shows the normal default and accepts one-line variants:

```text
【1】潜在学员需求诊断　【已解锁】
    默认难度：正常
    输入 1 开始；也可以输入：1 简单｜1 困难
```

Difficulties are `简单`, `正常`, and `困难`. The selected difficulty is recorded in the session and report.

## 4. Universal turn engine

One session allows at most 20 effective learner turns. Customer opening, loading, viewing rules/permissions/tasks, pause/resume, input switching, and repeated coach output do not consume a turn.

The engine warns at turn 15 that the session is entering closure and at turn 18 that three turns remain. Turn 20 must resolve to a clear outcome. If no clear outcome exists because learner turns were repetitive, verbose, irrelevant, or non-progressing, the learner outcome is `推进超时`, the customer outcome is `态度未明确`, and the next stage is not unlocked.

Each learner turn receives an internal quality value:

- `high`: concise, listens to prior evidence, gains material information or advances the stage, and contains no violation.
- `medium`: relevant and safe but broad, multi-part, or non-progressing.
- `low`: repeats known information, ignores the customer, rambles, asks irrelevant questions, overloads the customer, pitches without permission, or adds no meaningful evidence.

Medium resets both streaks. High resets the low streak. Low resets the high streak. Severe policy or ethics violations bypass ordinary quality and trigger their defined failure.

### 4.1 Easy

The persona has one main motivation and one main obstacle, and discloses evidence more readily. Three consecutive high-quality turns trigger internal `impulse` and player-visible `客户决策热度上升`. It lasts at most two learner turns, makes a valid next-step invitation more likely to be accepted, and ends immediately on a low-quality turn or violation. It never bypasses policy, fit, permission, or explicit customer boundaries.

### 4.2 Normal

No impulse or low-mood acceleration. Customer decisions follow persona truth, discovered evidence, and barriers. This is the default and reporting benchmark.

### 4.3 Hard

The persona can have layered obstacles, conflicting surface/real motives, or additional stakeholders. Two consecutive low-quality turns trigger internal `low_mood` and player-visible `客户沟通意愿下降`. One following high-quality turn recovers; medium keeps low mood; another low-quality turn accelerates a justified non-pass or failure. It cannot fabricate an outcome inconsistent with the persona or evidence.

## 5. DLC02-L01: 潜在学员需求诊断

### 5.1 Background and goal

The customer has just attended a salon, lecture, or other lead-generation class. The learner must use question-led selling to understand the customer and reach a qualified next action within 20 turns.

### 5.2 Evidence checklist

The session tracks whether the learner discovered: identity/industry/role/responsibility, attendance source, interest trigger, current situation, specific recent problem, impact, desired goal, past attempts, past learning experience, time constraints, funding/payment conditions, decision makers/influencers, project concerns, acceptable next action, and explicit boundaries.

### 5.3 Hidden persona truth

Every randomized persona contains 0–3 truth values for: real learning need, urgency, goal clarity, subjective motivation, time readiness, funding readiness, decision readiness, and paid-value orientation. It also contains evidence answers, surface statements, true motives, barriers, boundaries, free-benefit behavior, and best-fit next actions.

At every ending, including failure, the learner completes a customer-profile estimate. The result reports evidence completeness as a percentage and profile accuracy on eight 0–3 dimensions for a maximum of 24, showing truth, estimate, difference, and cited conversation evidence.

### 5.4 Passing next actions

A passing action must identify the counterpart, purpose, time/window, explicit customer consent, and contact permission. Valid tracks are: application form; formal open-class trial; professor interest consultation; school-leadership consultation on student status/academic administration/fees; academic-center thesis-topic consultation; detailed admissions consultation; external-relations/platform consultation; qualification/needs pre-assessment materials; or a joint consultation with a key decision maker.

### 5.5 L01 outcomes

- `通关`: a qualified next action is committed; unlock L02.
- `未通关·可培育`: real need exists but timing, funding, approval, or stakeholders are not ready.
- `未通关·动力不足`: learning is deferred until after the desired money/promotion result.
- `未通关·信息不足`: the customer continues verifying school/project credibility.
- `未通关·低价值索取`: repeated free salons, alumni benefits, or platform access without paid-learning intent; track a two-to-three-opportunity limit.
- `专业收场`: the learner correctly respects mismatch or a boundary; capability may score well, but L02 remains locked.
- `彻底失败`: explicit aversion, no-contact request, complaint, or relationship damage.
- `推进超时`: no clear attitude by turn 20 due to ineffective progression.

Only `通关` unlocks DLC02-L02. Other DLCs keep their existing progression contract unless separately redesigned.

## 6. DLC02-L02: 报名政策与价格谈判

### 6.1 Entry presentation

Immediately show a Chinese “恭喜晋级” card, background, known school rules, stakeholder authority table, and mission. Then load and play the customer opening without another start confirmation. If L01 passed through a different track, a time-advance card explains that preliminary consultation has finished and the customer now returns for enrollment details.

### 6.2 Training school rules

This is a fictional training policy, not real-school or legal advice:

- Application submission is not formal registration.
- Payment has a five-calendar-day cooling period only before formal registration.
- After formal registration, refunds are normally unavailable; exceptional review cannot be promised.
- One deferred-entry request may be submitted to academic administration; approval cannot be promised.
- Admissions staff cannot privately discount, rebate, or gift paid services.
- Installments require an official published plan.
- Scholarships require formal application and committee review; no result, ratio, or amount can be promised or deducted in advance.
- Financial aid is separate, requires supporting materials, and is decided by the academic-center director or professor.
- Combined-program pricing requires completing the combination; withdrawal recalculates earlier discounts, and a formally registered later stage is non-refundable.
- Special payment/resource/cooperation conditions require written leadership approval.

### 6.3 Authority matrix

- Admissions: explain standard rules, collect materials, schedule consultations, submit requests, and progress the process.
- Finance/academic administration: fees, payment, registration status, cooling period, refund and deferment confirmation.
- Scholarship committee: scholarship eligibility, percentage, and amount.
- Academic-center director/professor: aid, research direction, and academic support.
- School leadership: special payment, resource cooperation, and exception approval.

### 6.4 Personas

L02 randomizes among: boss/large-bargain/refund-risk; high-achiever/scholarship-entitlement; employee/price-sensitive/bundle-arbitrage; company-funded/invoice/approval; and resource-cooperation/company-visit/alumni-site. Each contains willingness, true concern, prohibited request temptations, valid routes, authority owner, and conditional-commitment language.

### 6.5 L02 passing outcomes

- `正常报名`: materials, policy acknowledgement, and standard or official installment payment.
- `奖学金流程`: formal application accepted without promised result.
- `助学金流程`: proper submission and academic authority review without promised result.
- `特殊条件审批`: condition is specific and lawful; the customer explicitly commits to enroll/pay if approved; admissions makes no promise and submits to the correct approver. Admissions work is complete regardless of the later approval result.

### 6.6 L02 non-pass and failures

Non-pass includes continued consideration, comparison without action, information-only scholarship/aid interest, special conditions without definite conditional enrollment, unresolved payment/company/stakeholder issues, professional close, relationship termination, or turn-20 timeout.

Immediate severe failure includes any-time refund promises, guaranteed scholarship/aid/discount, concealed registration refund limits, private rebates, “register now and refund later”, falsified or blurred policy, guaranteed admission/graduation/thesis/career outcome, fake invoice assistance, or other illegal/unethical action.

## 7. Scoring and records

All stages retain the common eight-dimensional 0–24 capability score and independent customer outcome. Logs add difficulty, turn count, quality counts, longest high/low streak, impulse/low-mood triggers, timeout, customer result, learner result, red lines, violations, and input modes.

L01 adds evidence completeness percentage and eight-dimensional 0–24 profile accuracy. L02 adds eight 0–3 policy-negotiation dimensions: true-concern diagnosis, policy accuracy, authority boundary, risk disclosure, price/value communication, compliant option design, negotiation stability, and compliant close.

High scores never automatically mean stage passage. Customer result, learner capability, policy compliance, and progression are stored separately.

## 8. Player-visible HUD and commands

Per-turn HUD contains stage/difficulty/turn, visible turn quality, current discovery phase, remaining turns, text/microphone guidance, and player commands. It never shows hidden persona values, trust/probability, branch IDs, tooling, or internal reasoning.

Supported non-turn commands: `查看任务`, `查看规则`, `查看权限`, `暂停`, `继续`, `结束并复盘`, `/voice`, and `/text`.

## 9. Acceptance criteria

Automated tests must prove: Chinese title/menu/status vocabulary; no technical leakage; stage selection starts immediately; voice help is persistent; 20-turn hard cap; warnings at 15/18; non-turn commands do not consume turns; exact easy/hard streak triggers and resets; normal has neither state; policy cannot be bypassed by impulse; L01 profile comparison is produced for every ending; only a qualified L01 action unlocks L02; L02 conditional approval requires a definite enroll/pay commitment and correct authority; severe promises fail immediately; all legacy assets/docs/tests remain; all manifests parse and reference nonempty files.

Human acceptance must cover a fresh-install startup, L01 easy/normal/hard, one failed L01 with profile reconstruction, L02 rules briefing, all four passing L02 paths, one special-condition non-pass, one professional close, one immediate severe failure, voice/text switching, and an exact turn-20 timeout.
