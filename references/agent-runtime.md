# Agent-native customer and coach runtime

## Responsibility split

The host Agent's current model performs all live semantic work: understanding the learner, choosing a scenario branch, acting the customer, and coaching. Python performs only deterministic support work: real media playback, progress, logs, reports, updates, and tests.

Never start `roleplay.py` for practice. Never call a second vendor-specific model API. Never replace a learner turn with a fixed “我听到了，请继续澄清” response.

## Session state

Maintain across all turns:

- DLC, stage, customer identity, difficulty, branch, turn, and opening variant;
- v0.3 scenario state: defense/trust/openness/decision or each participant's support;
- customer facts disclosed, facts still hidden, explicit boundaries, and permission state;
- learner evidence, red-line count, prompt count, input modes, and audio IDs already used;
- four-stage discovery evidence: current state, need, problem/impact, solution permission;

Typed text and host speech transcripts update the same state. Switching input modality never replays the opening or forgets evidence.

## Response decision

For each learner turn:

1. classify the learner behavior against the selected scenario's trigger table;
2. prefer a fitting unused branch variant and apply its state change;
3. if no branch exactly matches, compose a customer response consistent with the persona and current state, then select the closest non-contradictory fixed spoken line;
4. do not reveal hidden motives before the learner earns disclosure through questions;
5. let customer decisions remain autonomous, including refusal, delay, mismatch, or referral.

The spoken fixed line may be shorter than the display reply, but they must communicate the same intent. Fixed audio is the presentation layer, not the reasoning engine.

## Media truthfulness

Execute the packaged player. `"ok": true` means playback occurred or was successfully launched. Any other result must be surfaced as a text fallback. A Markdown link, image, or attachment is not evidence of playback.
