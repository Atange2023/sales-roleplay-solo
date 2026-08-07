# Gameplay flow

## Startup and navigation

Play boot music, show the bilingual character title, explain the objective, then show numbered DLC choices. After a DLC choice, show its numbered stages. Selecting an unlocked stage and optional difficulty immediately loads and begins it; never add a separate start confirmation.

All installed DLCs are independently selectable. Locks apply only within each DLC. Player-visible statuses and instructions are Chinese.

## Common turn rules

Every session has at most 20 effective learner turns. Customer openings, loading, coach output, viewing task/rules/permissions, pause/resume, finish, and input switching do not consume a turn.

Classify each learner response:

- `high`: concise, listens to known evidence, obtains material new information or advances the stage, and contains no violation.
- `medium`: relevant and safe but broad, multi-part, or non-progressing.
- `low`: repeats known facts, ignores the customer, rambles, asks irrelevant questions, overloads the customer, pitches without permission, or gains nothing meaningful.

Medium resets both streaks; high resets the low streak; low resets the high streak. Warn at turn 15 that closure should begin and at turn 18 that three effective turns remain. If turn 20 ends without a justified customer decision, record learner `推进超时`, customer `态度未明确`, and no unlock.

## Difficulty

- `简单`: one main motive and obstacle; evidence is easier to earn. Three consecutive high turns trigger `客户决策热度上升` for no more than two turns. A low turn ends it immediately.
- `正常`: no mood acceleration; this is the default benchmark.
- `困难`: layered motives or stakeholders. Two consecutive low turns trigger `客户沟通意愿下降`. A following high turn recovers, medium holds, and another low raises a justified non-pass risk.

Mood affects pacing only. It never bypasses customer boundaries, policy, authority, consent, fit, or ethics.

## Stage catalog

- DLC01-L01: manufacturing single-customer formal visit; preserve v0.3 branch pacing and review.
- DLC01-L02: manufacturing three-person solution meeting; preserve separate role support and voices.
- DLC02-L01: potential-student needs diagnosis; see [dlc02-stage1.md](dlc02-stage1.md).
- DLC02-L02: enrollment policy and price negotiation; see [dlc02-stage2.md](dlc02-stage2.md).

Recognize `暂停`, `继续`, `沉浸模式`, `教学模式`, and `结束并复盘`. Pausing preserves state. Default teaching mode shows parenthetical analysis, improvement advice, better wording, and progress after every customer turn.

## Common cues

- `stage_clear` → play `stage-clear`.
- `professional_exit` → play `professional-exit`; unlocking depends on the stage configuration.
- `needs_practice` or `推进超时` → no unlock; offer same-stage retry.
- `game_over` or a severe red line → play `game-over`; identify the verified mistake.
- perfect 24/24 → additionally play `achievement`; it never changes the customer result or unlock rule.
