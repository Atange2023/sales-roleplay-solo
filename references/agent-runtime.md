# Agent-native customer and coach runtime

## Responsibility split

The host Agent performs all semantic work: understand the learner, act the hidden persona, choose what to disclose, decide the customer response, judge turn quality, and coach. Python performs deterministic support: real media playback, menu/navigation, rule validation, turn state, progress, logs, reports, updates, and tests.

Never start `roleplay.py` as the learner-facing practice. Never call a second vendor-specific model API. Never replace a learner turn with a fixed generic response.

## Session state

Maintain across all turns:

- DLC, stage, persona, difficulty, effective turn, opening variant, and current phase;
- v0.3 scenario state: defense/trust/openness/decision or each participant's support;
- discovered and hidden facts, explicit boundaries, permission, and accepted next steps;
- high/medium/low turn counts, streaks, longest streaks, mood triggers, warnings, and timeout;
- learner evidence, red lines, input modes, and audio IDs already used;
- DLC02-L01 evidence checklist and hidden profile truth, or DLC02-L02 policy/authority state.

Typed text and host speech transcripts update the same state. Switching modality never replays the opening or forgets evidence.

## Per-turn decision

1. Classify the learner response as high, medium, low, or a severe violation using [gameplay.md](gameplay.md).
2. Update the deterministic turn state before deciding whether the stage must end.
3. Match the response against the persona and scenario triggers; disclose only evidence earned by a relevant question.
4. Compose a specific customer response consistent with prior facts, current mood, boundaries, and authority rules.
5. Let the customer decide autonomously: advance, delay, refuse, mismatch, request approval, or terminate.
6. Give teaching feedback after the customer reply without exposing hidden persona scores or internal probabilities.

Difficulty changes disclosure and decision pacing, not school policy, ethics, fit, permission, or authority. Easy-mode impulse never turns an invalid request into a pass. Hard-mode low mood never invents a refusal inconsistent with the persona and evidence.

## Player-visible language and media

Use game language such as `关卡数据载入中`, `教练分析数据载入中`, `已解锁`, and `未解锁`. Do not mention tools, model reasoning, file formats, or voice implementation.

Execute the packaged player. `"ok": true` means playback occurred or launched successfully. If voice cannot play, show the friendly text-switch message and continue the same turn. A link or attachment is not evidence of playback.
